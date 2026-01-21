from jmcomic import *
from jmcomic.cl import JmcomicUI

# 下方填入你要下载的本子的id，一行一个，每行的首尾可以有空白字符
jm_albums = '''
    JM563776
 JM562379
 JM554317
 JM540438
 JM543574
 JM543526
JM542524
JM542642
JM528766
 JM524082
 JM523410
 JM524064
 JM523574
 JM522020
 JM522353
 JM522369
 JM522373
 JM484965
JM519654
 JM515238
JM510359
 JM511852
 JM508547
 JM507774
JM507309
 JM507357
JM506941
 JM500350
 JM499284
 JM499440
 JM497543
 JM480825
 JM1250812
 JM1248555
JM1236579
 JM1236513
 JM1228265
 JM1229882
 JM1229310
 JM1225227
JM1223395
 JM1219487
 JM1213673
 JM1209004
JM1208727
 JM1200150
JM1178143
 JM1140945
JM1099826
 JM1070379
 JM1069010
 JM1050587
 JM1038343
JM1024355
 JM646866
 JM590960
JM530478
JM510359
 JM502158
 JM446749
 JM501682
 JM498666
 JM487811
JM481316
 JM477829
 JM461970
 JM462709
 JM456926
 JM453122
 JM425981
 JM419287
 JM418173
 JM418787
JM413173
 JM410784
 JM409854
JM408422
JM401891
 JM401581
 JM401192
 JM369854
JM360332
 JM349464
JM348126
 JM356448
 JM322373
 JM308022
 JM308023
 JM302215
 JM296079
 JM295953
 JM286521
 JM276734
 JM247561
JM250272
 JM243469
 JM244101
 JM179290
 JM192471
 JM99367
 JM89056
 JM70436
 JM79510
 JM27481
 JM14551
 JM9116
 JM2366
 JM1374
 JM1228785
JM644633
 JM604661
JM542657
 JM557573
 JM475261
 JM306828
 JM180312
 JM495239
 JM494146
 JM494910
 JM490864
JM488591
 JM482982
 JM472620
JM482807
 JM481966
 JM471870
 JM467973
 JM469447
 JM466414
 JM465328
 JM467371
 JM453579
 JM454599
 JM454427
 JM1224769
JM1215913
 JM1213677
 JM1116957
 JM1045171
 JM1018596
 JM1113272
JM1194296
 JM546303
 JM567258
 JM604081
 JM589034
 JM540468





















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
