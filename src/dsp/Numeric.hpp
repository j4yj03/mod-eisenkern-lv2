// SPDX-License-Identifier: MIT
// Shared numeric/transcendental kernels of the Eisenkern transformer core.
// Transferred from mod-1175-lv2 (Green Stripe 76) src/dsp/GreenStripe.hpp;
// operation order is mirrored by the EEL2 engine so both engines stay
// bit-equal, see docs/DSP.md.
#ifndef EISENKERN_NUMERIC_HPP
#define EISENKERN_NUMERIC_HPP

#include <algorithm>
#include <cmath>

namespace eisenkern {

inline double bounded(double x, double lo, double hi) {
    return std::max(lo, std::min(hi, x));
}
inline double finiteOr(double x, double fallback = 0.0) {
    return std::isfinite(x) ? x : fallback;
}
// Shared transcendental kernels with mirrored EEL2 operation order, so both
// engines stay bit-equal through parameter mapping and nonlinear solvers.
inline double seriesLog(double g) {
    double x = g < 1.0e-15 ? 1.0e-15 : g;
    int k = 0;
    while (x >= 2.0) { x *= 0.5; ++k; }
    while (x < 1.0) { x += x; --k; }
    const double y = (x - 1.0) / (x + 1.0);
    const double y2 = y * y;
    double acc = 0.034482758620689655;
    acc = y2 * acc + 0.037037037037037035;
    acc = y2 * acc + 0.040000000000000001;
    acc = y2 * acc + 0.043478260869565216;
    acc = y2 * acc + 0.047619047619047616;
    acc = y2 * acc + 0.052631578947368418;
    acc = y2 * acc + 0.058823529411764705;
    acc = y2 * acc + 0.066666666666666666;
    acc = y2 * acc + 0.076923076923076927;
    acc = y2 * acc + 0.090909090909090912;
    acc = y2 * acc + 0.1111111111111111;
    acc = y2 * acc + 0.14285714285714285;
    acc = y2 * acc + 0.20000000000000001;
    acc = y2 * acc + 0.33333333333333331;
    return k * 0.6931471805599453 + 2.0 * y * (1.0 + y2 * acc);
}
inline double seriesExp(double x) {
    const int k = static_cast<int>(std::floor(x / 0.6931471805599453 + 0.5));
    const double r = x - k * 0.6931471805599453;
    double acc = 1.1470745597729725e-11;
    acc = r * acc + 1.6059043836821613e-10;
    acc = r * acc + 2.08767569878681e-09;
    acc = r * acc + 2.505210838544172e-08;
    acc = r * acc + 2.7557319223985888e-07;
    acc = r * acc + 2.7557319223985893e-06;
    acc = r * acc + 2.4801587301587302e-05;
    acc = r * acc + 0.00019841269841269841;
    acc = r * acc + 0.0013888888888888889;
    acc = r * acc + 0.0083333333333333332;
    acc = r * acc + 0.041666666666666664;
    acc = r * acc + 0.16666666666666666;
    acc = r * acc + 0.5;
    acc = r * acc + 1.0;
    acc = r * acc + 1.0;
    double result = acc;
    int e = k;
    while (e > 0) { result += result; --e; }
    while (e < 0) { result *= 0.5; ++e; }
    return result;
}

// [7/6] Pade tanh approximation. Same function for signal and bias cancellation.
// Formula/properties discussed by J. Tom Schroeder, approximating-tanh (2026).
inline double dbGain(double db) { return seriesExp(db * 0.1151292546497022842); }
inline double gainDb(double gain) {
    return 8.68588963806503655 * seriesLog(gain);
}
inline double zap(double x) { return std::abs(x) < 1.0e-30 ? 0.0 : x; }

}  // namespace eisenkern

#endif
