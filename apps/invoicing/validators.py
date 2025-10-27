from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator


class AustralianBusinessValidator:
    
    @staticmethod
    def validate_abn(value):
        clean_value = value.replace(' ', '')
        
        if len(clean_value) != 11 or not clean_value.isdigit():
            raise ValidationError('ABN must be 11 digits')
        
        weights = [10, 1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
        abn_sum = sum(
            (int(clean_value[i]) - (1 if i == 0 else 0)) * weights[i] 
            for i in range(11)
        )
        
        if abn_sum % 89 != 0:
            raise ValidationError('Invalid ABN checksum')
        
        return clean_value
    
    @staticmethod
    def validate_acn(value):
        clean_value = value.replace(' ', '')
        
        if len(clean_value) != 9 or not clean_value.isdigit():
            raise ValidationError('ACN must be 9 digits')
        
        return clean_value
    
    @staticmethod
    def format_abn(value):
        clean = value.replace(' ', '')
        return f"{clean[:2]} {clean[2:5]} {clean[5:8]} {clean[8:11]}"
    
    @staticmethod
    def format_acn(value):
        clean = value.replace(' ', '')
        return f"{clean[:3]} {clean[3:6]} {clean[6:9]}"
    
    @staticmethod
    def format_bsb(value):
        clean = value.replace('-', '')
        return f"{clean[:3]}-{clean[3:6]}"


class AustralianPostcodeValidator(RegexValidator):
    regex = r'^\d{4}$'
    message = 'Australian postcode must be 4 digits'


class BSBValidator(RegexValidator):
    regex = r'^\d{3}-?\d{3}$'
    message = 'BSB must be 6 digits in format XXX-XXX'


class ABNValidator(RegexValidator):
    regex = r'^\d{2}\s?\d{3}\s?\d{3}\s?\d{3}$'
    message = 'ABN must be 11 digits in format XX XXX XXX XXX'


class ACNValidator(RegexValidator):
    regex = r'^\d{3}\s?\d{3}\s?\d{3}$'
    message = 'ACN must be 9 digits in format XXX XXX XXX'


class AustralianAccountNumberValidator(RegexValidator):
    regex = r'^\d{6,10}$'
    message = 'Account number must be 6-10 digits'
