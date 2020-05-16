#pragma once
#include <string.h>
#include <stdint.h>
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


static inline const char * df_parser(uint8_t n) {
    switch(n) {
    case DF_ORIGIN:
        return "DF_ORIGIN";
    case DF_SYMBOLIC:
        return "DF_SYMBOLIC";
    case DF_TEXTREL:
        return "DF_TEXTREL";
    case DF_BIND_NOW:
        return "DF_BIND_NOW";
    case DF_STATIC_TLS:
        return "DF_STATIC_TLS";
    default:
        return "Unknown";
    }
}


static inline const char * df_1_parser(uint8_t n) {
    switch(n) {
    case DF_1_NOW:
        return "DF_1_NOW";
    case DF_1_GLOBAL:
        return "DF_1_GLOBAL";
    case DF_1_GROUP:
        return "DF_1_GROUP";
    case DF_1_NODELETE:
        return "DF_1_NODELETE";
    case DF_1_LOADFLTR:
        return "DF_1_LOADFLTR";
    case DF_1_INITFIRST:
        return "DF_1_INITFIRST";
    default:
        return "Unknown";
    }
}
