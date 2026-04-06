export const defaultMapping = {
  orderNo: 'order_id',
  customerName: 'customer_name',
  customerEmail: 'email',
  phone: 'phone',
  address: 'shipping_address',
  amount: 'total_amount',
  productName: 'product_name'
};

export function mapFields(source = {}, mapping = defaultMapping) {
  return Object.entries(mapping).reduce((acc, [mailKey, erpKey]) => {
    acc[erpKey] = source[mailKey] ?? null;
    return acc;
  }, {});
}

export function validateConsistency(beforeData, afterData, keys = []) {
  const checkKeys = keys.length ? keys : Object.keys(beforeData);

  return checkKeys.every((key) => {
    const before = beforeData[key];
    const after = afterData[key];
    return String(before ?? '') === String(after ?? '');
  });
}
