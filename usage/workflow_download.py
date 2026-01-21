from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
   JM427068
 JM510520
 JM480118
 JM473995
 JM467112
JM375186
JM391477
 JM359850
 JM305377
 JM32636
 JM321031
 JM1232228
 JM1248278
 JM1242227
 JM1205551
JM1188841
 JM1117868
 JM1071654
 JM1067742
JM651801
 JM1047379
 JM605918
JM644801
 JM589023
 JM579761
 JM561818
 JM578870
JM557306
 JM547272
 JM530989
 JM521250
 JM508034
 JM426254
 JM333401
 JM509014
 JM556856
 JM527777
 JM651903
 JM1016791
 JM1216734
 JM1127148
JM1098219
 JM1127146
 JM1127147
 JM1016531
 JM1084692
 JM358974
 JM357977
 JM359566
 JM485718
 JM302247
 JM357660
JM292026
 JM288432
 JM209729
 JM194474
 JM269105
 JM121783
 JM121785
 JM121784
 JM1181769
 JM1202969
 JM1205555
 JM1150194
 JM1150193
 JM1130526
 JM1130525
 JM1071521
 JM1101032
JM1083588
 JM651704
 JM649482
 JM647292
 JM646854
 JM646665
 JM592688
 JM592693
 JM645562
 JM495034
 JM478541
 JM470428
 JM216870
 JM456916
 JM448670
 JM439562
 JM439126
 JM433020
 JM419972
 JM389739
 JM358988
 JM356005
 JM344980
 JM350772
 JM344524
 JM341501
JM309268
 JM304756
 JM306827
 JM302364
 JM292761
 JM295006
JM292444
 JM292374
JM285631
 JM289442
 JM280900
 JM281048
 JM275130
 JM278537
 JM275497
 JM260994
 JM259854
 JM259515
 JM259154
 JM250392
 JM243361
JM250595
 JM225191
 JM229961
 JM239498
 JM221670
 JM217710
 JM222461
 JM223147
 JM1248023
 JM1248491
 JM1247718
 JM1238774
 JM1238357
JM1233940
 JM559682
 JM1226548
 JM1196025
 JM1194004
 JM1191296
 JM1203240
 JM1190444
JM1184501
 JM1128115
 JM1111595
 JM1054627
JM438260
 JM470932
 JM476099
 JM114267
 JM295247
 JM188442
 JM287640
 JM269664
 JM317473
 JM335945
JM372742
 JM1248076
 JM1241195
 JM1238654
 JM1021473
JM1204830
JM1197427
JM1021470
JM1021118
 JM1021107
JM496740
 JM519118
 JM453908
 JM430711
 JM405731
 JM404600
 JM364605
 JM267446
JM347110
 JM315753
 JM296689
 JM220555
 JM195026
JM187822
JM208066
 JM180834
 JM135793
 JM81450
 JM1242420
 JM1238254
 JM1241777
 JM1237882
 JM1237236
 JM1222332
 JM1209542
 JM1194672
JM1187984
 JM1131420
JM1015890
 JM1121832
 JM1121537
 JM1075775
 JM1079942
 JM1068576
 JM1052254
 JM1052863
 JM1050734
 JM1049564
 JM1044816
 JM1032291
 JM1228431
 JM1228458
 JM1228279
 JM1228068
 JM1227612
 JM1225248
 JM1225201
 JM1224854
 JM1205455
 JM1203533
 JM1202093
JM1200726
 JM1201115
 JM1201119
 JM1200121
 JM1196549
JM1195982
JM1193754
JM1194235
 JM1187997
 JM1184493
 JM99431
 JM1209328
 JM1224462
 JM1248778
 JM459244
 JM402127
 JM364863
 JM263115
 JM337283
 JM1127476
 JM1069322
 JM426267
 JM565640
 JM481422
 JM465308
 JM355901
JM1093041
 JM1205068
 JM461624
 JM626309
JM364175
 JM143891
 JM517723
 JM1160548
 JM1159374
 JM1159286
JM1152922
 JM1151593
 JM1079518
 JM1120022
 JM1068433
JM1066885
 JM643498
 JM638329
 JM625265
 JM625261
JM554239
 JM477923
 JM419615
 JM407098
 JM1069109
 JM395797
 JM426382
JM1245663
JM1203267
 JM1220340
 JM1140952
 JM1179404
 JM1188997
 JM1198951
 JM1077403
 JM1079852
 JM1098901
 JM1125759
 JM1048792
 JM1037729
 JM651792
 JM650605
 JM635367
 JM638933
 JM582136
 JM577953
 JM573222
 JM455622
 JM466372
 JM530279
 JM338706
JM299579
JM309635
 JM298123



















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
