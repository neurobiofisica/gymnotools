#include <stdio.h>
#include <stdlib.h>
#include <string.h>

struct module_t {
    const char *name;
    const char *arghelp;
    int (*main)(int argc, char **argv);
};

static int test_main(int argc, char **argv) {
    printf("from test\n");
    for(int i = 0; i < argc; i++) {
        printf("argv[%d] = '%s'\n", i, argv[i]);
    }
    return 0;
}

module_t modules[] = {
    {"test", "[args ...]", test_main},
    {NULL, NULL, NULL}
};

static void usage(const char *progname) {
    fprintf(stderr, "usage: %s module [arguments]\n", progname);
    fprintf(stderr, "available modules:\n");
    for(int i = 0; modules[i].name != NULL; i++) {
        fprintf(stderr, "  %s %s\n", modules[i].name, modules[i].arghelp);
    }
}

int main(int argc, char **argv)
{
    if(argc >= 2) {
        for(int i = 0; modules[i].name != NULL; i++) {
            if(!strcasecmp(argv[1], modules[i].name)) {
                return modules[i].main(argc - 1, &argv[1]);
            }
        }
    }
    usage(argv[0]);
    return 1;
}
