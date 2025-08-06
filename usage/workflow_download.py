from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
 JM436669
 JM432910
 JM432590
JM364628
 JM349776
JM314015
 JM293990
 JM96646
 JM59271
JM1196537
JM1189360
 JM1171904
 JM1187729
 JM1069292
 JM87435
 JM1201689
 JM1201606
 JM559682
 JM1191296
JM1111595
 JM1089519
JM1044007
 JM1054627
 JM646452
 JM188442
 JM1095886
 JM1100624
 JM596983
JM565606
 JM1042317
 JM506944
 JM441914
JM372778
 JM321985
 JM303184
 JM122402
 JM1201193
 JM1200199
JM1198313
 JM1203063
 JM1195625
 JM1196614
 JM1175421
JM1175727
JM1176057
JM1144701
 JM460834
 JM604197
JM548223
 JM537115
JM505718
JM504996
JM469459
 JM466388
 JM466714
 JM467289
 JM462700
 JM442110
 JM433288
 JM443588
JM432680
 JM398702
 JM385957
 JM359566
JM361264
 JM1146884
 JM1101265
 JM1101031
JM1053611
JM1030844
 JM1032505
 JM632756
 JM563737
JM551669
 JM467103
 JM465327
JM433028
 JM409667
 JM397181
JM304525
 JM304121
 JM529215
 JM604661
JM557573
JM556369
JM430211
 JM438025
 JM1087878
 JM546303
 JM567258
 JM589034
 JM604081
JM540468
JM480118
 JM479801
 JM375186
JM391477
 JM326361
JM321031
 JM305377
 JM1107772
 JM405731
JM475261
 JM638158
 JM462501
JM293866
 JM1200544
 JM1199887
 JM1190094
 JM1189579
JM1192935
JM1175703
 JM1148430
 JM1144534
 JM1126650
 JM488736
JM1123445
JM78158
 JM1202353
JM1196608
 JM1196685
JM1195643
JM1193175
JM1191267
 JM1189723
JM1189724
JM1185383
 JM1169699
 JM1132434
JM1125812
 JM1126320
 JM1125594










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
