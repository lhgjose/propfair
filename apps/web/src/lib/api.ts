const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ListingSearchParams {
  city?: string;
  neighborhood?: string;
  min_price?: number;
  max_price?: number;
  bedrooms?: number;
  bathrooms?: number;
  min_area?: number;
  max_area?: number;
  estrato?: number;
  page?: number;
  page_size?: number;
}

export interface Listing {
  id: string;
  title: string;
  description: string | null;
  price: number;
  admin_fee: number | null;
  bedrooms: number;
  bathrooms: number;
  parking_spaces: number;
  area: number;
  estrato: number | null;
  address: string;
  neighborhood: string;
  city: string;
  latitude: number;
  longitude: number;
  source: string;
  url: string;
  images: string[];
  is_active: boolean;
  first_seen_at: string;
  last_seen_at: string;
}

export interface PaginatedListings {
  items: Listing[];
  total: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export async function searchListings(
  params: ListingSearchParams
): Promise<PaginatedListings> {
  const searchParams = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null) {
      searchParams.append(key, String(value));
    }
  });

  const response = await fetch(
    `${API_BASE_URL}/api/v1/listings?${searchParams.toString()}`
  );

  if (!response.ok) {
    throw new Error("Failed to fetch listings");
  }

  return response.json();
}
