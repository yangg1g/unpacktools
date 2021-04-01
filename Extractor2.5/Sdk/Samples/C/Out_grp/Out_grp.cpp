#include <windows.h>

#include "..\..\..\api\inc\ExtrDefs.h"


BOOL __stdcall Save(TSaveGroupfileParams *Params)
{
  typedef struct {
    char Id[12];
    DWORD Count;
  } THeader;

  typedef struct {
    char Name[12];
    DWORD Size;
  } TFileHeader;

  THeader Header;
  TFileHeader FileHeader;
  TGetFileInfo *Info;
  int i, StartPos;
  DWORD written;

  strncpy(Header.Id, "KenSilverman", sizeof(Header.Id));
  Header.Count = Params->Count;
  
  if (!WriteFile(Params->FileHandle, &Header, sizeof(THeader), &written, NULL)) return FALSE;

  StartPos = sizeof(THeader);

  for (i = 0; i < Params->Count; i++) {
    if (Params->Stop) return FALSE;
    Info = Params->GetFile(i);

    memset(&FileHeader, 0, sizeof(TFileHeader));
    strncpy(FileHeader.Name, Info->Name, sizeof(TFileHeader));
    FileHeader.Size = Info->Size;
    if (!WriteFile(Params->FileHandle, &FileHeader, sizeof(TFileHeader), &written, NULL)) return FALSE;
    StartPos += sizeof(TFileHeader);
  }

  for (i = 0; i < Params->Count; i++) {
    if (Params->Stop) return FALSE;
    Info = Params->GetFile(i);
    Params->SetInfo(Info->Name);
    if (!Params->ExtractFile(i, StartPos)) return FALSE;
    StartPos += Info->Size;
    Params->FileDone += Info->Size;
    Params->ShowStatus();
  }

  return TRUE;
}


void __stdcall About(HWND Handle)
{
  MessageBox(Handle, "Duke Nukem 3D pack plugin", "Information", MB_OK);
}
  
TPluginInfo Plugin = {
  API_VER,
  FT_GROUPFILE,
  "GRP",
  "Duke Nukem 3D pack",
  1,
  NULL,
  Save,
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
