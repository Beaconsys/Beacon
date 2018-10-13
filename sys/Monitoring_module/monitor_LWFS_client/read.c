//[2016-07-27 15:34:33] T [fuse-bridge.c:1967:fuse_writev_cbk] lwfs-fuse: 18049: WRITE => 131072/131072,2096627712/2096627712
#include <stdio.h>
int main(){
  int y, M, d, h, m, s, ln, op, unknown, opu, size, size2;
  long long off, off2;
  scanf("[%d-%d-%d %d:%d:%d] T [fuse-bridge.c:%d:%s] lwfs-fuse: %d: %s => %d/%d,%lld,%lld", &y, &M, &d, &h, &m, &s, &ln, &op, &unknown, &opu, &size, &size2, &off, &off2);
  printf("%d %d %d %d %d %d %d %s %d %s %d %d %lld %lld", y, M, d, h, m, s, ln, op, unknown, opu, size, size2);
  return 0;
}
