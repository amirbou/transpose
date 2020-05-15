#pragma once
#include <string.h>
#include "test.h"


static inline const char * logpriority_parser(enum LogPriority n) {
    switch(n) {
    case LOG_UNKNOWN:
        return "LOG_UNKNOWN";
    case LOG_DEFAULT:
        return "LOG_DEFAULT";
    case LOG_VERBOSE:
        return "LOG_VERBOSE";
    case LOG_DEBUG:
        return "LOG_DEBUG";
    case LOG_INFO:
        return "LOG_INFO";
    case LOG_WARN:
        return "LOG_WARN";
    case LOG_ERROR:
        return "LOG_ERROR";
    default:
        return "Unknown";
    }
}


static inline const char * log_id_parser(enum log_id n) {
    switch(n) {
    case LOG_ID_MIN:
        return "LOG_ID_MIN_OR_MAIN";
    case LOG_ID_RADIO:
        return "LOG_ID_RADIO";
    case LOG_ID_EVENTS:
        return "LOG_ID_EVENTS";
    case LOG_ID_SYSTEM:
        return "LOG_ID_SYSTEM";
    case LOG_ID_CRASH:
        return "LOG_ID_CRASH";
    case LOG_ID_STATS:
        return "LOG_ID_STATS";
    case LOG_ID_SECURITY:
        return "LOG_ID_SECURITY";
    case LOG_ID_KERNEL:
        return "LOG_ID_KERNEL";
    case LOG_ID_MAX:
        return "LOG_ID_MAX";
    default:
        return "Unknown";
    }
}


#define DF_MAX_LEN (14)
#define DF_PARSER(n, buf) do {\
    switch(n) {\
    case DF_ORIGIN:\
            strcpy(buf, "DF_ORIGIN");\
            break;\
    case DF_SYMBOLIC:\
            strcpy(buf, "DF_SYMBOLIC");\
            break;\
    case DF_TEXTREL:\
            strcpy(buf, "DF_TEXTREL");\
            break;\
    case DF_BIND_NOW:\
            strcpy(buf, "DF_BIND_NOW");\
            break;\
    case DF_STATIC_TLS:\
            strcpy(buf, "DF_STATIC_TLS");\
            break;\
    default:\
            strcpy(buf, "Unknown");\
            break;\
    }\
} while (0);


#define DF_1_MAX_LEN (15)
#define DF_1_PARSER(n, buf) do {\
    switch(n) {\
    case DF_1_NOW:\
            strcpy(buf, "DF_1_NOW");\
            break;\
    case DF_1_GLOBAL:\
            strcpy(buf, "DF_1_GLOBAL");\
            break;\
    case DF_1_GROUP:\
            strcpy(buf, "DF_1_GROUP");\
            break;\
    case DF_1_NODELETE:\
            strcpy(buf, "DF_1_NODELETE");\
            break;\
    case DF_1_LOADFLTR:\
            strcpy(buf, "DF_1_LOADFLTR");\
            break;\
    case DF_1_INITFIRST:\
            strcpy(buf, "DF_1_INITFIRST");\
            break;\
    default:\
            strcpy(buf, "Unknown");\
            break;\
    }\
} while (0);
