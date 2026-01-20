from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
   JM1247682
 JM1247706
 JM1247866
 JM1247730
 JM1247718
JM1247712
 JM1247702
JM1247710
JM1247709
 JM1247711
 JM1247697
JM1247692
 JM1195674
JM1247691
JM1247859
 JM1247708
 JM1247777
JM1247788
JM1247794
JM1247791
 JM1247790
JM1247786
 JM1247774
JM1247789
 JM1247849
JM1247783
JM1236488
 JM1247646
JM1012940
JM1247586
 JM1247584
JM1247582
 JM1247559
JM1247558
 JM1247552
JM1247557
 JM1241398
 JM1037621
JM1247386
JM1247406
 JM1247395
JM1247397
 JM1247371
 JM1247409
JM1247394
 JM1247537
JM1247505
JM1247361
JM1247358
JM1247343
 JM1247325
 JM1247323
JM1247321
 JM1247318
JM1247314
 JM1247311
 JM1247154
JM1247199
 JM1247109
JM1247153
 JM1247145
JM1247161
JM1246996
 JM1246988
 JM1246995
 JM1247000
 JM1247006
 JM1247220
 JM1247166
 JM1247160
 JM1247147
JM1246880
 JM1246878
 JM1246874
 JM1246954
JM1246945
JM1246915
 JM1246914
JM1246902
 JM1246900
 JM1246905
 JM1246899
 JM1246898
 JM1246894
 JM1246890
 JM1246889
 JM1246888
JM1246886
 JM1246877
JM1246617
 JM1246555
 JM1246542
JM1246535
JM1246528
 JM1246525
 JM1246515
 JM1246500
 JM1246492
JM1246496
 JM1246495
 JM1246488
JM1246477
 JM1246463
JM1246366
JM1246259
 JM1246261
JM1246257
JM1246258
 JM1246255
 JM1246248
JM1246247
 JM1246245
 JM1246243
JM1246238
JM1246234
 JM1246232
 JM1246059
 JM1246227
JM1246222
JM551074
 JM1246054
JM1246051
 JM1246084
 JM1246208
JM1246211
 JM1246089
JM1246204
 JM1246092
JM1246198
 JM1246088
JM1246056
 JM1246058
 JM1246080
 JM1246052
 JM1246049
JM1246048
 JM1245969
 JM1245821
 JM1245837
 JM1245741
JM1245744
 JM1245666
JM1245711
 JM1245616
JM1245517
JM1245493













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
