import torch

from services.bertmodel import BertModelConfig, BertModelTaskExecuter


def test_bert():
    # 配置参数
    bert_executor = BertModelTaskExecuter(
        BertModelConfig(
            device="cuda:1" if torch.cuda.is_available() else "cpu",
            model_path="./models/bert",
            tokenizer_path="./models/bert",
            input_column="描述",
            output_column="新评分",
        )
    )

    # 加载模型和分词器
    bert_executor.init()

    # 生成任务
    _, payload = bert_executor.create_task(
        file_name="data1600withrand.xlsx",
        input_path="./data/data1600withrand.xlsx",
        output_path="./data/data1600withrand_output.xlsx",
    )

    # 执行任务
    bert_executor.process(payload, lambda x: x) # type: ignore
