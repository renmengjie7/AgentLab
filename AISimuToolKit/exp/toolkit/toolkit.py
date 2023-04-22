class ExternalToolkit:
    def __init__(self, toolkit_config=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_id = None
        self.toolkit_config = toolkit_config
        self.toolkit_api = toolkit_config["api"]
        self.target_name = toolkit_config["target"]

    def chat(self, message: str, *args, **kwargs):
        """
        :param message:
        :param args:
        :param kwargs:
        :return:
        """
        pass

    def get_backend(self):
        return self.toolkit_config["name"]

    def transfor_name2id(self, name2id):
        self.target_id = [name2id[item] for item in self.target_name]

    def get(self, **kwargs):
        raise NotImplementedError

    def post(self, **kwargs):
        raise NotImplementedError

    def finetune(self, **kwargs):
        raise NotImplementedError

    def get_target(self):
        return self.target_id


class RecommendSystem(ExternalToolkit):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_recommend(self, id: int, message: str, *args, **kwargs) -> str:
        """

        :param id:
        :param message:
        :param args:
        :param kwargs:
        :return:
        """
        pass
