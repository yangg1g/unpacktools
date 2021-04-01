
#include <windows.h>

#include "..\..\..\api\inc\ExtrDefs.h"


BOOL __stdcall Load(TLoadGroupfileParams *Params)
{
  DWORD FileTableSize;
  char FileName[256];
  DWORD Size,Pos;
  DWORD read;
  char c;

  if (!ReadFile(Params->FileHandle, &FileTableSize, sizeof(FileTableSize), &read, NULL)) return 0;
  Pos = sizeof(FileTableSize) + FileTableSize;
  Params->FileDone = sizeof(FileTableSize);
  while (FileTableSize > 0) {
    FileName[0] = '\0';
    do {
      if (!ReadFile(Params->FileHandle, &c, 1, &read, 0)) return 0;
      if (c == '\0') break;
      strncat(FileName, &c, 1);
    } while (1);
    if (!ReadFile(Params->FileHandle, &Size, 4, &read, 0)) return 0;
    if (Size > 0)
      if (!Params->AddFile(Params->FileName, FileName, Pos, Size, NULL, 0)) return 0;
    Pos += Size;
    FileTableSize -= strlen(FileName) + 1 + 4;
    Params->FileDone += strlen(FileName) + 1 + 4 + Size;
    Params->ShowStatus();
  }
  return 1;
}

void __stdcall About(HWND Handle)
{
  MessageBox(Handle, "ICQ Sound Scheme Plugin", "Information", MB_OK);
}

TPluginInfo Plugin = {
  API_VER,
  FT_GROUPFILE,
  "SCM",
  "ICQ Sound Scheme",
  0,
  NULL,
  Load,
  About,
  NULL
};

extern "C" __declspec(dllexport) TPluginInfo* __stdcall GetPluginInfo(TServiceProcs *ServiceProcs)
{
  return &Plugin;
}


BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fwdreason, LPVOID lpvReserved)
{
  return 1;
}

