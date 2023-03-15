
@staticmethod
def find_model_name(table):
    model_name = table.split('_')[-1]
    total_count = len(table.split('_')) - 1
    app_labeled = table.split('_')[0:total_count]
    if len(app_labeled) == 1:
        app_label = app_labeled[0]
    else:
        app_label = '_'.join(app_labeled)

    return model_name, app_label
