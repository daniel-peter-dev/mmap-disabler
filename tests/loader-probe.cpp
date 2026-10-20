// SPDX-License-Identifier: GPL-3.0-or-later
// This shell-process probe opens no audio stream and captures no sound.
#include "../third_party/jami/jamiplugin.h"
#include <dlfcn.h>
#include <cstdio>
int main(int argc,char** argv) {
    if(argc!=2)return 2;
    auto a=dlopen("libaaudio.so",RTLD_NOW|RTLD_LOCAL);
    if(!a)return 3;
    auto get=reinterpret_cast<int(*)()>(dlsym(a,"AAudio_getMMapPolicy"));
    if(!get)return 4;
    auto p=dlopen(argv[1],RTLD_NOW|RTLD_LOCAL);
    if(!p){std::printf("loader error: %s\n",dlerror());return 5;}
    auto init=reinterpret_cast<JAMI_PluginInitFunc>(dlsym(p,"JAMI_dynPluginInit"));
    if(!init)return 6;
    if(init(nullptr)!=nullptr)return 7;
    JAMI_PluginAPI api{};api.version={JAMI_PLUGIN_ABI_VERSION,JAMI_PLUGIN_API_VERSION};
    const int before=get();auto exit=init(&api);const int after=get();
    if(!exit||after!=1)return 8;
    exit();const int afterUnload=get();
    std::printf("policy before=%d loaded=%d after-exit=%d; no audio opened\n",before,after,afterUnload);
    return afterUnload==1 ? 0 : 9;
}
