// SPDX-License-Identifier: GPL-3.0-or-later
#pragma once
namespace jami_mmap {
using GetPolicy = int (*)();
using SetPolicy = int (*)(int);
// No operation when disabled=false: preserve the Android/Jami default policy.
inline int apply(bool disabled, GetPolicy get, SetPolicy set) {
    if (!disabled) return 0;
    if (!get || !set) return -2;
    const int previous = get();
    if (previous < 0) return -3;
    if (set(1) != 0) return -4; // AAUDIO_POLICY_NEVER
    if (get() != 1) { set(previous); return -5; }
    return 1;
}
}
