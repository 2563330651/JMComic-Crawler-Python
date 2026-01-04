from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
 JM1226548
 JM1236340
 JM1210154
 JM1235013
JM1234989
 JM1235123
 JM1235234
JM1233946
 JM1234363
JM1235004
 JM1235121
JM1233949
 JM1233940
JM1234025
 JM1235130
 JM1235500
 JM1234359
JM1235978
JM1236162
JM1235699
 JM1235148
JM1234916
JM1235119
 JM1236122
JM1235228
 JM1235403
JM1235705
 JM1236018
 JM1233941
 JM1234011
JM1236142
 JM474
JM574
JM1235499
JM1235887
JM1235335
JM1235031
JM1233877
 JM1234023
JM1235975
JM1234297
 JM1235329
 JM1235665
JM1236086
 JM1235150
 JM1234929
 JM1235696
JM1236201
 JM1235317
 JM1235154
 JM1234017
 JM1236291
JM1235767
 JM1235659
JM1235878
JM1233910
JM1236108
JM1236488
 JM1235229
JM1234352
 JM1233908
 JM1236021
 JM1234332
 JM1234982
JM1235881
 JM1235640
 JM1236033
 JM1235225
JM1234930
JM1235647
 JM1236209
 JM1234907
 JM1235327
 JM1236509
 JM1235889
 JM1236208
JM1235989
 JM1236421
 JM1236513
JM1236572
 JM518074
 JM1114752
 JM356488
JM1236505
JM1236512
JM1236520
 JM1236522
JM1236602
 JM1227590
JM1226818
JM1226588
 JM1225796
JM1225434
JM1224961
JM1224957
 JM1224803
JM1224145
JM1222858
JM1222883
JM1222480
JM1220905
 JM1220461
JM1218457
JM1090939
JM553496
JM587697
 JM422841
JM602615
JM1214213
 JM1201622
JM1205429
 JM1224720
JM1193711
 JM1140929
JM1091474
JM1086610
JM1069757
 JM1043983
 JM1013359
 JM1015996
JM1013245
 JM650868
 JM625794
 JM595465
 JM553403
JM529621
 JM428361
 JM419976
 JM389752
 JM1221139
JM1220737
 JM1220422
JM1220341
JM1206332
 JM1214545
 JM1130526
JM529580
 JM554925
 JM648028
 JM485676

 JM256830
JM429107
JM260499
JM301239
JM241841
JM228443
JM595465












'''

# 单独下载章节
jm_photos = '''



'''


def env(name, default, trim=('[]', '""', "''")):
    import os
    value = os.getenv(name, None)
    if value is None or value == '':
        return default

    for pair in trim:
        if value.startswith(pair[0]) and value.endswith(pair[1]):
            value = value[1:-1]

    return value


def get_id_set(env_name, given):
    aid_set = set()
    for text in [
        given,
        (env(env_name, '')).replace('-', '\n'),
    ]:
        aid_set.update(str_to_set(text))

    return aid_set


def main():
    album_id_set = get_id_set('JM_ALBUM_IDS', jm_albums)
    photo_id_set = get_id_set('JM_PHOTO_IDS', jm_photos)

    helper = JmcomicUI()
    helper.album_id_list = list(album_id_set)
    helper.photo_id_list = list(photo_id_set)

    option = get_option()
    helper.run(option)
    option.call_all_plugin('after_download')


def get_option():
    # 读取 option 配置文件
    option = create_option(os.path.abspath(os.path.join(__file__, '../../assets/option/option_workflow_download.yml')))

    # 支持工作流覆盖配置文件的配置
    cover_option_config(option)

    # 把请求错误的html下载到文件，方便GitHub Actions下载查看日志
    log_before_raise()

    return option


def cover_option_config(option: JmOption):
    dir_rule = env('DIR_RULE', None)
    if dir_rule is not None:
        the_old = option.dir_rule
        the_new = DirRule(dir_rule, base_dir=the_old.base_dir)
        option.dir_rule = the_new

    impl = env('CLIENT_IMPL', None)
    if impl is not None:
        option.client.impl = impl

    suffix = env('IMAGE_SUFFIX', None)
    if suffix is not None:
        option.download.image.suffix = fix_suffix(suffix)


def log_before_raise():
    jm_download_dir = env('JM_DOWNLOAD_DIR', workspace())
    mkdir_if_not_exists(jm_download_dir)

    def decide_filepath(e):
        resp = e.context.get(ExceptionTool.CONTEXT_KEY_RESP, None)

        if resp is None:
            suffix = str(time_stamp())
        else:
            suffix = resp.url

        name = '-'.join(
            fix_windir_name(it)
            for it in [
                e.description,
                current_thread().name,
                suffix
            ]
        )

        path = f'{jm_download_dir}/【出错了】{name}.log'
        return path

    def exception_listener(e: JmcomicException):
        """
        异常监听器，实现了在 GitHub Actions 下，把请求错误的信息下载到文件，方便调试和通知使用者
        """
        # 决定要写入的文件路径
        path = decide_filepath(e)

        # 准备内容
        content = [
            str(type(e)),
            e.msg,
        ]
        for k, v in e.context.items():
            content.append(f'{k}: {v}')

        # resp.text
        resp = e.context.get(ExceptionTool.CONTEXT_KEY_RESP, None)
        if resp:
            content.append(f'响应文本: {resp.text}')

        # 写文件
        write_text(path, '\n'.join(content))

    JmModuleConfig.register_exception_listener(JmcomicException, exception_listener)


if __name__ == '__main__':
    main()
