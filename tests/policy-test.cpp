#include "../src/mmap-policy.h"
static int policy=2, writes=0, failSet=0, ignoreSet=0;
static int get(){return policy;}
static int set(int p){++writes; if(failSet)return -1; if(!ignoreSet)policy=p; return 0;}
int main(){
    using jami_mmap::apply;
    if(apply(false,nullptr,nullptr)!=0||writes!=0)return 1;
    if(apply(true,nullptr,set)!=-2||writes!=0)return 2;
    if(apply(true,get,nullptr)!=-2||writes!=0)return 3;
    policy=-1;if(apply(true,get,set)!=-3||writes!=0)return 4;
    policy=2;failSet=1;if(apply(true,get,set)!=-4||policy!=2)return 5;
    failSet=0;ignoreSet=1;if(apply(true,get,set)!=-5||policy!=2)return 6;
    ignoreSet=0;if(apply(true,get,set)!=1||policy!=1)return 7;
    if(apply(true,get,set)!=1||policy!=1)return 8;
    const int before=writes;if(apply(false,get,set)!=0||writes!=before)return 9;
    return 0;
}
