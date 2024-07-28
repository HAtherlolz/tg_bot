from cfg.celery_conf import celery_app


@celery_app.task()
def check_msg():
    # TODO: logic of checking if msg has a reply
    print("============== CELERY IS WORKING ==============")
