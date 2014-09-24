# metadata.py
"""
File containing metadata information for WW2100 model run
"""
class UnknownFileType(BaseException):
    pass

##model_run = 'MIROC'
def define_model_run():
    import xlrd
    model_book = xlrd.open_workbook('Master File.xls')
    Refer = str(model_book.sheet_by_index(0).col_values(0)[1])      #find the reference model type
    if Refer[-12:-9] == 'Ref':
        reference = 'MIROC'
    elif Refer[-16:-9] == 'LowClim':
        reference = 'GFDL'
    elif Refer[-20:-9] == 'FireSupress':
        reference = 'AltFire'
    elif Refer[-17:-9] == 'HighClim':
        reference = 'HADLEY'
    elif Refer[-16:-9] == 'HighPop':
        reference = 'AltPop'
    elif Refer[-18:-9] == 'UrbExpand':
        reference = 'AltUGAThresh'
    else:
        raise UnknownFileType()
    Compare = str(model_book.sheet_by_index(0).col_values(1)[1])    #find the comparative model type
    if Compare[-12:-9] == 'Ref':
        comparative = 'MIROC'
    elif Compare[-16:-9] == 'LowClim':
        comparative = 'GFDL'
    elif Compare[-21:-9] == 'FireSuppress':
        comparative = 'AltFire'
    elif Compare[-17:-9] == 'HighClim':
        comparative = 'HADLEY'
    elif Compare[-16:-9] == 'HighPop':
        comparative = 'AltPop'
    elif Compare[-18:-9] == 'UrbExpand':
        comparative = 'AltUGAThresh'
    else:
        raise UnknownFileType()
    model_run = comparative + ' climate minus ' + reference
    return model_run

model_run = define_model_run()  #run the program and get the metadata
