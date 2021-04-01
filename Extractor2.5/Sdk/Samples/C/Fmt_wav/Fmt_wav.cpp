
#include <windows.h>

#include "..\..\..\api\inc\ExtrDefs.h"


BOOL __stdcall Test(void *Buf)
{
  return *(DWORD *)((DWORD)Buf + 8) == 'WAVE';
//  return *(DWORD *)((DWORD)Buf + 8) == 0x45564157;
//  COMPARE(Buf, "WAVE", 4, 8);
//  return Compare(Buf, "WAVE", 4, 8);  
}

BOOL __stdcall Load(TLoadFormatParams *Params)
{
  typedef struct {
    char Id[4];
    DWORD Length;
    char WaveId[4];
  } THeader;

  THeader Header;
  DWORD read;

  ReadFile(Params->FileHandle, &Header, sizeof(THeader), &read, 0);
  if (strncmp(Header.Id, "RIFF", 4) != 0) return 0;
  Params->FileSize = Header.Length + 8;
  Params->FileInfo = "wav file information";
  Params->FileExt = "wav";
  return 1;
}

void __stdcall About(HWND Handle)
{
  MessageBox(Handle, "Windows Wave File Plugin", "Information", MB_OK);
}

TPluginInfo Plugin = {
  API_VER,
  FT_SOUND,
  "WAV",
  "Windows Wave File",
  85,
  Test,
  Load,
  About,
  NULL
};

extern "C" __declspec(dllexport) TPluginInfo* __stdcall GetPluginInfo(TServiceProcs *ServiceProcs)
{
  return(&Plugin);
}


BOOL WINAPI DllMain(HINSTANCE hinstDLL, DWORD fwdreason, LPVOID lpvReserved)
{
  return 1;
}

