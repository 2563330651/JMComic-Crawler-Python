from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
 JM1200726
 JM1097060
JM1198942
JM543965
JM377486
JM1201690
 JM1195649
 JM1195599
JM1180620
JM1200546
JM1195971
 JM1200044
 JM1192925
 JM1150189
 JM1124846
 JM564039
JM564038
JM513355
 JM513624
 JM497109
 JM499801
 JM496401
 JM467969
JM459567
 JM463962
JM456396
 JM442072
 JM440132
JM440131
 JM440128
 JM440127
 JM438272
JM432022
JM432000
JM431402
 JM431830
 JM423768
JM400597
 JM399384
JM398008
JM394996
JM379966
 JM374816
 JM355964
JM362443
 JM369831
 JM355278
 JM350779
 JM350777
JM337008
JM293613
JM298457
JM291046
JM289306
JM279765
 JM282561
 JM285104
JM279766
 JM252522
 JM269634
JM256408
 JM37508
 JM151662
 JM1199764
 JM1200121
JM1198516
 JM1195982
 JM1189098
 JM1187997
 JM1195975
 JM1194529
 JM1192507
 JM1189661
 JM1162620
 JM1137872
 JM430639
 JM426571
 JM374300
JM387612
JM221448
JM129749
JM1202085
 JM1179803
 JM1112881
 JM1099829
 JM1200862
JM1175956
 JM1123448
JM1094460
 JM1098902
JM1075775
 JM1059527
 JM1060419
 JM1194672
 JM1185399
 JM1183730
 JM1181774
 JM1181773
JM1181761
JM1180616
 JM1176220
 JM1060417
 JM1060416
JM1060415
 JM1059011
 JM588310
 JM180878
JM212295
JM203621
JM181869
 JM1201491
 JM622497
JM1112173
 JM1091278
JM1102416
 JM1090729
 JM644538
 JM346703
 JM344294
JM344519
 JM295247
JM146316
 JM124078
 JM102361
JM95735
JM34090
 JM33071
JM26128
 JM4744
 JM1198570
 JM1199848
JM1196820
JM1195883
 JM1195339
JM1194957
 JM508123
 JM420117
 JM1027121
 JM499631
 JM1194637
JM1076900
 JM627712
 JM621936
 JM560464
 JM509315
 JM416370
 JM368068
JM230088
 JM1079257
 JM1075775
 JM1069500
 JM1067721
 JM638650
 JM613966
 JM1189969
 JM1188771
JM1118540
 JM1116957
 JM1083982
 JM1045515
JM1045241
JM1038320
JM1029384
 JM635956
 JM616364
 JM1028399
JM568649
 JM563490
JM558109
 JM474031









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
