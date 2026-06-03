#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>

#include "hidapi.h"
#include "hidapi_darwin.h"

static int call_feature(hid_device *dev, unsigned char dev_idx, unsigned char feature_idx,
                        unsigned char func, unsigned char *out, size_t out_len) {
    unsigned char buf[32];
    memset(buf, 0, sizeof(buf));
    buf[0] = 0x11;
    buf[1] = dev_idx;
    buf[2] = feature_idx;
    buf[3] = func;
    buf[4] = 0x0F;
    int w = hid_write(dev, buf, 20);
    if (w < 0) {
        return -1;
    }
    int r = hid_read_timeout(dev, out, (int)out_len, 1000);
    return r;
}

int main(int argc, char **argv) {
    const char *path = "DevSrvsID:4294971833";
    if (argc > 1) {
        path = argv[1];
    }

    if (hid_init() != 0) {
        fprintf(stderr, "hid_init failed\n");
        return 1;
    }

    hid_darwin_set_open_exclusive(0);

    hid_device *dev = hid_open_path(path);
    if (!dev) {
        fprintf(stderr, "hid_open_path failed for %s\n", path);
        struct hid_device_info *list = hid_enumerate(0x046d, 0xc332);
        for (struct hid_device_info *cur = list; cur; cur = cur->next) {
            if (cur->usage_page == 0xff00) {
                fprintf(stderr, "trying ff00 path %s usage 0x%x\n", cur->path, cur->usage);
                dev = hid_open_path(cur->path);
                if (dev) {
                    path = cur->path;
                    break;
                }
            }
        }
        hid_free_enumeration(list);
    }

    if (!dev) {
        fprintf(stderr, "could not open any HID++ interface\n");
        return 2;
    }

    printf("opened %s\n", path);

    unsigned char resp[32];
    for (unsigned char idx = 0xFF; idx <= 0xFF; idx++) {
        memset(resp, 0, sizeof(resp));
        int r = call_feature(dev, idx, 0, 0, resp, sizeof(resp));
        printf("dev_idx 0x%02x write/read r=%d", idx, r);
        if (r > 0) {
            printf(" data:");
            for (int i = 0; i < r && i < 20; i++) {
                printf(" %02x", resp[i]);
            }
        }
        printf("\n");
        if (r > 0 && resp[4] != 0) {
            break;
        }
    }

    hid_close(dev);
    hid_exit();
    return 0;
}
