export type FuelType = 'Gasoil50' | 'SansPlomb';

export interface FuelData {
  id?: number;
  timestamp: string;
  station_id?: string;
  fuel_type: FuelType;
  price_tnd: number;
  official_price_tnd: number;
  stock_liters: number;
  capacity_liters: number;
  sales_last_5min_liters: number;
}
