import threading


# Inheriting the base class 'Thread'
class AsyncWriteGDF(threading.Thread):

    def __init__(self):

        # calling superclass init
        threading.Thread.__init__(self)

    def save(self, gdf_object, output_filename):

        gdf_object.to_file(
            output_filename, layer='validation', driver="GPKG")
        return
