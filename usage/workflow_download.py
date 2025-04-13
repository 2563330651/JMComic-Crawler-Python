from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
JM1084704
JM1113942
JM1085143
JM583232
JM560563
JM551952
JM544133
JM544134
JM544135
JM1101040
JM1047379
JM637759
JM1043486
JM612729
JM528275
JM528229
JM524908
JM503452
JM478525
JM476447
JM367179
JM339748
JM305430
JM276176
JM206228
JM151438
JM651704
JM649482
JM647292
JM646854
JM1123435
JM1101032
JM1084701
JM1083588
JM1071521
JM1021016
JM1013132
JM1013096
JM646665
JM645665
JM645562
JM611617
JM600071
JM592693
JM592688
JM216870
JM495034
JM478541
JM470428
JM456916
JM448670
JM439562
JM439126
JM434252
JM433020
JM428980
JM419972
JM414833
JM413542
JM393752
JM389739
JM351148
JM374561
JM358988
JM356005
JM350772
JM344980
JM344524
JM341501
JM337212
JM336504
JM323612
JM309268
JM306827
JM304756
JM302364
JM298257
JM295006
JM292761
JM292444
JM292374
JM289442
JM285631
JM281048
JM280900
JM278537
JM275497
JM275130
JM273370
JM260994
JM259854
JM259515
JM259154
JM256489
JM250595
JM250392
JM243361
JM239498
JM229961
JM224711
JM225191
JM223147
JM222461
JM221670
JM217710
JM1046534
JM1046258
JM616118
JM616123
JM609886
JM554303
JM525170
JM522013
JM520955
JM511623
JM479374
JM478595
JM119057
JM1073844
JM1071211
JM641435
JM641338
JM630593
JM545516
JM539456
JM515064
JM516074
JM473457
JM438243
JM415757
JM365568
JM361160
JM337391
JM281456
JM243897
JM71131
JM63807
JM3300
JM306825
JM303626
JM303625
JM302518
JM162661
JM118299
JM82578
JM121475
JM121210
JM73227
JM70523
JM67263
JM67241
JM65223
JM64509
JM62648
JM62312
JM61137
JM60984
JM57809
JM57081
JM56001
JM55129
JM50877
JM49261
JM49231
JM49232
JM45313
JM43275
JM41734
JM36907
JM27464
JM17351
JM16672
JM16670
JM16664
JM16662
JM16660
JM16656
JM16594
JM10471
JM1687
JM496
JM483
JM65969
JM639783
JM638597
JM601655
JM600103
JM570212
JM549758
JM515750
JM474300
JM471233
JM471225
JM431896
JM431847
JM431060
JM429593
JM304020
JM368829
JM317899
JM297084
JM1087897
JM1085138
JM1084882
JM1084881
JM1084880
JM1084879
JM1084878
JM1084877
JM1084407
JM1073208
JM1073215
JM567268
JM568663
JM568664
JM1073211
JM564521
JM502875
JM498476
JM439365
JM405321
JM392331
JM381772
JM323138
JM315073
JM286907
JM287029
JM229280
JM72360
JM71244





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
