import os
from django.conf import settings

dau_cau ="àáãạảăắằẳẵặâấầẩẫậèéẹẻẽêềếểễệđìíĩỉịòóõọỏôốồổỗộơớờởỡợùúũụủưứừửữựỳỵỷỹýÀÁÃẠẢĂẮẰẲẴẶÂẤẦẨẪẬÈÉẸẺẼÊỀẾỂỄỆĐÌÍĨỈỊÒÓÕỌỎÔỐỒỔỖỘƠỚỜỞỠỢÙÚŨỤỦƯỨỪỬỮỰỲỴỶỸÝ"
abc = dau_cau + "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ!\"#$%&\'()*+,-./:;?@[\\]^_`{|}~ "
# no duplicate char
assert len(set(abc)) == len(abc)
num_worker = 0

# data
data_path = "/root/textGenerator/source/out"
# train_dev_path = "/root/TA/data/clean/train_dev/"
current_path = os.path.dirname(__file__)
json_file_path = os.path.join(current_path, "desc3.json")
output_dir = os.path.join(current_path, "out")

test_mode = "test_annotated"
# test_path = "/root/TA/data/clean/"
# test_path = os.path.join("/root/TA/data/clean/", test_mode)

# basemodel
backend = "resnet18"
# snapshot = os.path.join(current_path, "out/crnn_resnet18_best")
snapshot = os.path.join(settings.BASE_DIR, "model/crnn_" + backend + "_best")

# logging
num_write_input_img = 30
output_csv = False
output_image = True
output_transform = True

# model config
# input_size = "1920x128"
input_size = "3840x128"
base_lr = 1e-3
batch_size = 40
dev_batch_size = 100
dropout = 0.25

# CNN
num_filter = 512
downrate = 2 ** 5

# LSTM
lstm_input_size = 512
lstm_hidden_size = 256
lstm_num_layers = 1
lstm_dropout = 0

