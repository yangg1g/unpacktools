
#include <windows.h>


BOOL Compare(void *buf, char *s, int len, int pos)
{
  (char *)buf += pos;
  while (*s == *((char *)(buf))) {
    len--;
    if (len == 0) break;
    s++;
    ((char *)buf)++;
  }
  return len == 0;
}
