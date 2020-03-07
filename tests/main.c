#include <stdio.h>

#include "test.h"
#include "expected_result.h"

int main(void)
{
    char buf[LOGPRIORITY_MAX_LEN] = { 0 };
    LOGPRIORITY_PARSER(LOG_VERBOSE, buf);
    printf("LOG_VERBOSE=%s\n", buf);
    
    char buf2[LOG_ID_MAX_LEN] = { 0 };
    LOG_ID_PARSER(LOG_ID_MIN, buf2);
    printf("LOG_ID_MIN=%s    (expected LOG_ID_MIN_OF_MAIN)\n", buf2);

    char buf3[DF_MAX_LEN] = { 0 };
    DF_PARSER(DF_BIND_NOW, buf3);
    printf("DF_BIND_NOW=%s\n", buf3);

    char buf4[DF_1_MAX_LEN] = { 0 };
    DF_1_PARSER(DF_1_INITFIRST, buf4);
    printf("DF_1_INITFIRST=%s\n", buf4);

}
