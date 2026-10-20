// SPDX-License-Identifier: GPL-3.0-or-later
#include "../third_party/jami/jamiplugin.h"
#include "mmap-policy.h"
#include <android/log.h>
#include <dlfcn.h>

namespace {
constexpr const char* tag = "JamiMmapExtension";
void leavePolicyUntilRestart() {
    // Never change a process-wide policy while other call streams may be open.
    __android_log_print(ANDROID_LOG_INFO, tag,
        "Unloaded; restart Jami to restore Android's default MMAP policy");
}
}
extern "C" __attribute__((visibility("default"))) JAMI_PluginExitFunc
JAMI_dynPluginInit(const JAMI_PluginAPI* api) {
    if (!api || api->version.abi != JAMI_PLUGIN_ABI_VERSION) {
        __android_log_print(ANDROID_LOG_ERROR, tag, "Unsupported extension ABI");
        return nullptr;
    }
    // Retain the handle: AAudio owns the per-process policy and may own streams.
    static void* lib = dlopen("libaaudio.so", RTLD_NOW | RTLD_LOCAL);
    if (!lib) {
        __android_log_print(ANDROID_LOG_ERROR, tag, "Cannot load libaaudio.so");
        return nullptr;
    }
    const auto get = reinterpret_cast<jami_mmap::GetPolicy>(dlsym(lib, "AAudio_getMMapPolicy"));
    const auto set = reinterpret_cast<jami_mmap::SetPolicy>(dlsym(lib, "AAudio_setMMapPolicy"));
    const int result = jami_mmap::apply(true, get, set);
    __android_log_print(result == 1 ? ANDROID_LOG_INFO : ANDROID_LOG_ERROR, tag,
        "MMAP disable result=%d; new streams only; restart after removal", result);
    return result == 1 ? leavePolicyUntilRestart : nullptr;
}
