def mask_value(value, mask_rule):
    # Example: mask_rule = 'XXXX XXXX {last4}'
    if '{last4}' in mask_rule:
        return mask_rule.replace('{last4}', value[-4:])
    if '{last7}' in mask_rule:
        return mask_rule.replace('{last7}', value[-7:])
    return mask_rule
