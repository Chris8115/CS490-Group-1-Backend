from flask_restx import fields

class RestModel:
    def __init__(self, namespace):
        self.namespace=namespace
    
    def get_cats(self):
        data_model={
            "data":fields.List(
                fields.Nested(self._resp())
            ),
            "message":fields.String()
        }
        return self.namespace.model('get_cats_model',data_model )
    
    def _resp(self):
        data_model={
            "id":fields.String(),
            "name":fields.String()
        }
        return self.namespace.model('a_cat_model',data_model )