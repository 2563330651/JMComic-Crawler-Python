from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
  JM1224981
 JM1224867
 JM1224854
 JM1224850
 JM1224846
 JM1224847
 JM1222498
 JM1224787
 JM1085860
 JM1224636
 JM1224368
 JM1224311
 JM1224145
 JM1223946
 JM1222883
 JM1222825
 JM1222789
 JM1222156
JM1222006
 JM1209098
 JM1221141
 JM1220922
 JM1220768
 JM1220781
 JM1220475
 JM1220473
 JM1220111
 JM1220551
JM1220383
 JM1219819
 JM1219432
 JM1219437
 JM1219075
 JM1219049
 JM1218640
JM1218671
 JM1218906
 JM1217636
 JM1217637
 JM1217536
JM1217435
 JM1217465
 JM1217428
JM1205817
 JM1216964
 JM1216757
 JM1216460
JM1216231
 JM1216304
 JM1216346
 JM1215993
 JM1215602
 JM1215607
 JM1215271
 JM1215066
 JM1215087
 JM1214730
 JM1214025
 JM1213324
 JM1212299
 JM1212311
 JM1211501
 JM1211298
 JM1210811
 JM1249240
 JM1249054
 JM102658
 JM1248601
 JM1246914
 JM339033
 JM1242154
 JM1240699
 JM1240960
 JM1241580
 JM1240347
JM1239054
 JM1238099
 JM1237970
 JM1237621
 JM1233703
 JM1235380
 JM1230332
 JM1230095
 JM1229555
 JM1228279
JM1228276
 JM1227425
 JM1227372
 JM1225315
 JM1220637
 JM1213655
JM1210482
 JM1207962
 JM1204634
JM1203633
 JM1203250
 JM1232450
 JM1226039
JM1226038
 JM1205178
 JM1200381
 JM1190476
 JM1127414
 JM1098170
 JM1095541
JM1075996
 JM1058215
 JM1025760
 JM650274
 JM640505
 JM640413
JM639420
 JM620224
 JM586455
 JM544367
 JM539919
 JM518500
 JM508784
 JM467504
 JM432869
 JM419124
 JM426256
 JM402943
 JM400461
 JM342552
 JM345040
 JM353558
 JM340852
 JM340216
 JM298117
JM274473
JM241714
 JM180500
 JM1202084
 JM1202863
 JM1200510
 JM1200284
JM1200172
 JM1199910
 JM1199247
 JM1199148
 JM1198810
 JM1196608
JM1186817
 JM1145801
 JM1146983
JM1137723
 JM1144561
 JM1140100
 JM1128069
 JM1136877
 JM1096578
 JM1088740
 JM1081256
 JM1060165
 JM1062228
 JM643128
JM631049
 JM623260
JM1248649
 JM432596
JM1250534
JM1247325
 JM1027519
 JM473342
 JM1245650
 JM1245486
 JM1245335
 JM248002
 JM1241759
 JM1241498
 JM1233931
 JM1242589
 JM1212028
JM1204348
 JM1097764
 JM1117780
JM430363
JM1250585 












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
