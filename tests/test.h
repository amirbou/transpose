#pragma once
typedef enum LogPriority {
  LOG_UNKNOWN = 0,
  LOG_DEFAULT,
  LOG_VERBOSE,
  LOG_DEBUG,
  LOG_INFO,
  LOG_WARN,
  LOG_ERROR,
} LogPriority;

typedef enum log_id {
  LOG_ID_MIN = 0,
  LOG_ID_MAIN = 0,
  LOG_ID_RADIO = 1,
  LOG_ID_EVENTS = 2,
  LOG_ID_SYSTEM = 3,
  LOG_ID_CRASH = 4,
  LOG_ID_STATS = 5,
  LOG_ID_SECURITY = 6,
  LOG_ID_KERNEL = 7,

  LOG_ID_MAX
} log_id_t;

#define DF_ORIGIN     0x00000001
#define DF_SYMBOLIC   0x00000002
#define DF_TEXTREL    0x00000004
#define DF_BIND_NOW   0x00000008
#define DF_STATIC_TLS 0x00000010

#define DF_1_NOW        0x00000001 
#define DF_1_GLOBAL     0x00000002
#define DF_1_GROUP      0x00000004
#define DF_1_NODELETE   0x00000008
#define DF_1_LOADFLTR   0x00000010
#define DF_1_INITFIRST  0x00000020
