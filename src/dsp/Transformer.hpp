// SPDX-License-Identifier: MIT
// Load-coupled flux model from the independent offline reference, with bounded
// Newton iterations and matched-pole HF discretization; runtime contract in
// docs/DSP.md. Transferred from mod-1175-lv2 (Green Stripe 76)
// src/dsp/Transformer.hpp — transfer map and adaptations in docs/DSP.md.
#ifndef EISENKERN_TRANSFORMER_HPP
#define EISENKERN_TRANSFORMER_HPP

#include "Numeric.hpp"
#include "TransformerModels.hpp"

namespace eisenkern {

struct TransformerCoefficients {
    const transformer_model::Profile* p;
    double h, ra, denominator, relaxation, weights[14], memoryBound;
    double a1, a2, b0, b1, outputScale;
    double inv_lm_h, inv_relax_l_h, inv_relax_den, inv_den;
    double hf_knee, hf_fk, hf_sk, hf_target, hf_width;
    static double cosine(double x) {
        // Initialization only; identical fixed operation order in EEL2.
        const double x2 = x*x;
        double y = 1.0/6402373705728000.0;
        y = -1.0/20922789888000.0+x2*y;
        y = 1.0/87178291200.0+x2*y;
        y = -1.0/479001600.0+x2*y;
        y = 1.0/3628800.0+x2*y;
        y = -1.0/40320.0+x2*y;
        y = 1.0/720.0+x2*y;
        y = -1.0/24.0+x2*y;
        y = 0.5+x2*y;
        return 1.0-x2*y;
    }
    void prepare(double rate, unsigned modelIndex) {
        p = &transformer_model::profiles[modelIndex];
        h = 0.5/rate;
        ra = p->source_resistance_ohm+p->primary_resistance_ohm;
        const double rb = p->secondary_resistance_ohm+p->load_resistance_ohm;
        denominator = 1.0+ra/rb+ra*p->core_conductance_s;
        relaxation = h*6.283185307179586*p->relax_frequency_hz;
        memoryBound = 0;
        for (unsigned j=0; j<14; ++j) {
            weights[j] = p->hysteresis_enabled*p->hysteresis_stiffness_a_per_vs*
                seriesExp(p->hysteresis_slope*seriesLog(transformer_model::thresholds[j]/0.001));
            memoryBound += weights[j]*transformer_model::thresholds[j];
        }
        // Matched analog poles, then a minimum-phase real zero fitted at
        // min(20 kHz, 0.4 fs). Unlike raw Tustin this does not force a zero at
        // Nyquist when the analog corner is above Nyquist.
        const double w = 6.283185307179586*p->hf_frequency_hz/rate;
        const double decay = seriesExp(-std::min(60.0,w/(2.0*p->hf_q)));
        double angle = w*std::sqrt(1.0-1.0/(4.0*p->hf_q*p->hf_q));
        angle -= 6.283185307179586*std::floor(angle/6.283185307179586+0.5);
        a1 = -2.0*decay*cosine(angle); a2 = decay*decay;
        const double frequency = std::min(20000.0,rate*0.4);
        const double c = cosine(6.283185307179586*frequency/rate);
        const double r = frequency/p->hf_frequency_hz;
        const double magnitude2 = 1.0/((1.0-r*r)*(1.0-r*r)+r*r/(p->hf_q*p->hf_q));
        const double den2 = 1.0+a1*a1+a2*a2+2.0*a1*(1.0+a2)*c+2.0*a2*(2.0*c*c-1.0);
        const double sum = 1.0+a1+a2;
        const double product = (sum*sum-magnitude2*den2)/(2.0*(1.0-c));
        b0 = 0.5*(sum+std::sqrt(std::max(0.0,sum*sum-4.0*product)));
        b1 = sum-b0;
        outputScale = p->load_resistance_ohm/rb*p->fixed_output_normalization/p->source_volts_per_fs;
        inv_lm_h = 1.0/p->lm_h;
        inv_relax_l_h = 1.0/p->relax_l_h;
        inv_relax_den = 1.0/((1.0+relaxation)*p->relax_l_h);
        inv_den = 1.0/denominator;
        hf_knee = hf_fk = hf_sk = hf_target = hf_width = 0.0;
        if (p->family==1) {
            hf_knee = 0.98*p->flux_scale_vs;
            hf_fk = hf_knee*(1.0+p->saturation_strength*0.98/0.02)/p->lm_h;
            hf_sk = (1.0+p->saturation_strength*0.98/0.02+
                p->saturation_strength*0.98/(0.02*0.02))/p->lm_h;
            hf_target = 1.0/(p->lm_h*p->high_field_l_ratio);
            hf_width = std::max(0.000001,p->flux_scale_vs*0.01);
        }
    }
};

struct TransformerBank {
    TransformerCoefficients c[3][4];
    explicit TransformerBank(double rate) {
        for (unsigned os=0; os<3; ++os)
            for (unsigned m=0; m<4; ++m) c[os][m].prepare(rate*(1u<<os),m);
    }
};

// Opt-in diagnostic counter for the bounded solver. Compiled out unless
// EISENKERN_TRANSFORMER_STATS is defined, so no released build changes; the
// counter is a plain integer add and cannot alter the solved value. reset()
// clears it, so a mid-run model change or bypass restarts the count.
#ifdef EISENKERN_TRANSFORMER_STATS
struct TransformerSolverStats {
    unsigned iterations, samples, capped;
    unsigned stops_clamped[14];
    void clear() { iterations = samples = capped = 0;
                   for (unsigned j=0; j<14; ++j) stops_clamped[j]=0; }
};
#endif

struct TransformerCore {
    double flux, relax, voltage, stops[14], x1, y1, y2, px2;
#ifdef EISENKERN_TRANSFORMER_STATS
    TransformerSolverStats stats;
#endif
    void reset() {
        flux=relax=voltage=x1=y1=y2=px2=0;
        for (unsigned j=0; j<14; ++j) stops[j]=0;
#ifdef EISENKERN_TRANSFORMER_STATS
        stats.clear();
#endif
    }
    static double law(double x, const TransformerCoefficients& c, double& slope) {
        const transformer_model::Profile& p=*c.p;
        if (p.saturation_strength==0.0) {
            slope=c.inv_lm_h;
            return x*c.inv_lm_h;
        }
        const double u=std::abs(x)/p.flux_scale_vs;
        if (p.family==1) {
            if (u>0.98) {
                const double delta=std::abs(x)-c.hf_knee;
                const double e=seriesExp(-std::min(60.0,delta/c.hf_width));
                slope=c.hf_target+(c.hf_sk-c.hf_target)*e;
                const double value=c.hf_fk+c.hf_target*delta+
                    (c.hf_sk-c.hf_target)*c.hf_width*(1.0-e);
                return x>=0 ? value : -value;
            }
            const double d=1.0-u;
            slope=(1.0+p.saturation_strength*u/d+p.saturation_strength*u/(d*d))*c.inv_lm_h;
            return x*(1.0+p.saturation_strength*u/d)*c.inv_lm_h;
        }
        double nonlinear=1;
        for (unsigned i=1; i<static_cast<unsigned>(p.exponent); ++i) nonlinear*=u;
        nonlinear*=p.saturation_strength;
        slope=(1.0+p.exponent*nonlinear)*c.inv_lm_h;
        return x*(1.0+nonlinear)*c.inv_lm_h;
    }
    double current(double x, const TransformerCoefficients& c, double& derivative, bool advance) {
        double value=law(x,c,derivative);
        const double z=((1.0-c.relaxation)*relax+c.relaxation*(x+flux))/(1.0+c.relaxation);
        value+=(x-z)*c.inv_relax_l_h;
        derivative+=c.inv_relax_den;
        if (advance) relax=zap(z);
        if (c.p->hysteresis_enabled!=0.0) {
            for (unsigned j=0; j<14; ++j) {
                const double trial=stops[j]+x-flux;
                const double stop=bounded(trial,-transformer_model::thresholds[j],transformer_model::thresholds[j]);
                value+=c.weights[j]*stop;
                if (std::abs(trial)<transformer_model::thresholds[j]) derivative+=c.weights[j];
#ifdef EISENKERN_TRANSFORMER_STATS
                if (std::abs(trial)>=transformer_model::thresholds[j]) ++stats.stops_clamped[j];
#endif
                if (advance) stops[j]=zap(stop);
            }
        }
        return value;
    }
    double process(double input, const TransformerCoefficients& c) {
        const double source=input*c.p->source_volts_per_fs;
        const double rb=std::abs((1.0-c.relaxation)*relax+c.relaxation*flux)*
            c.inv_relax_den;
        const double bound=std::abs(flux+c.h*voltage)+c.h*
            (std::abs(source)+c.ra*(c.memoryBound+rb))*c.inv_den+1e-12;
        double lo=-bound, hi=bound;
        double x=bounded(flux+2.0*c.h*voltage+(flux-px2),lo,hi);
#ifdef EISENKERN_TRANSFORMER_STATS
        unsigned usedIterations=0;
#endif
        double derivative=0.0, i=0.0;
        bool converged=false;
        for (unsigned iteration=0; iteration<40; ++iteration) {
#ifdef EISENKERN_TRANSFORMER_STATS
            ++usedIterations;
#endif
            i=current(x,c,derivative,false);
            const double residual=x-flux-c.h*(voltage+(source-c.ra*i)*c.inv_den);
            if (std::abs(residual)<=1e-6*(1.0+std::abs(x))) { converged=true; break; }
            if (residual>0) hi=x; else lo=x;
            const double next=x-residual/(1.0+c.h*c.ra*derivative*c.inv_den);
            x=next>lo && next<hi ? next : 0.5*(lo+hi);
        }
#ifdef EISENKERN_TRANSFORMER_STATS
        stats.iterations+=usedIterations; ++stats.samples;
        if (usedIterations>=40) ++stats.capped;
#endif
        if (converged) {
            // Konvergiertes x: Wert/Ableitung sind identisch reproduzierbar;
            // nur die Zustands-Aktualisierung fehlt noch — ohne erneute
            // Auswertung von law()/Stops (bitidentische Formeln/Reihenfolge).
            const double z=((1.0-c.relaxation)*relax+c.relaxation*(x+flux))/
                (1.0+c.relaxation);
            relax=zap(z);
            if (c.p->hysteresis_enabled!=0.0) {
                for (unsigned j=0; j<14; ++j) {
                    const double trial=stops[j]+x-flux;
                    stops[j]=zap(bounded(trial,-transformer_model::thresholds[j],
                                         transformer_model::thresholds[j]));
                }
            }
        } else {
            i=current(x,c,derivative,true);
        }
        px2=flux; flux=zap(x); voltage=zap((source-c.ra*i)*c.inv_den);
        const double raw=voltage*c.outputScale;
        const double y=c.b0*raw+c.b1*x1-c.a1*y1-c.a2*y2;
        x1=raw; y2=y1; y1=zap(y);
        return y;
    }
};

struct TransformerStage {
    TransformerCore core;
    int active, requested;
    double blend;
    void reset(int model=0) { core.reset(); active=requested=model; blend=model ? 1.0 : 0.0; }
    double process(double x, int selected, const TransformerCoefficients* bank, double rate) {
        if (!active && !selected) return x;
        requested=selected;
        const double step=1.0/std::max(1.0,std::ceil(0.002*rate));
        if (active!=requested) {
            blend=std::max(0.0,blend-step);
            if (blend<=1e-12) { blend=0; active=requested; core.reset(); }
        } else blend=std::min(active ? 1.0 : 0.0,blend+step);
        if (!active) return x;
        const double y=core.process(x,bank[active-1]);
        return x+blend*(y-x);
    }
};

}  // namespace eisenkern

#endif
