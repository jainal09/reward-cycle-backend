import mongoengine
import globals


def global_init():
    mongoengine.register_connection(
        db=globals.DB,
        host=globals.MONGO_HOST,
        port=int(globals.PORT),
        alias='core',
    )
    mongoengine.connect(
        db=globals.DB,
        host=globals.MONGO_HOST,
        port=int(globals.PORT)
    )

