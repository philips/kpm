


def loop():
    test = {"spec": {"package": "ant31/rocketchat",
                     "namespace": "rocket",
                     "variables:": {"image": "rocketchat/rocketchat:latest"}
                     }
    }
    # watch for new kpm thirdparty
    unprocessed_tp = [test, test]
    for tp in unprocessed_tp:
        package = tp['spec']['package']
        namespace = tp['spec']['package']
