"use client";

import { useState, useCallback } from "react";
import { ListingFilters } from "@/components/listings/ListingFilters";
import { ListingCard } from "@/components/listings/ListingCard";
import { MapContainer } from "@/components/map/MapContainer";
import { searchListings, type Listing, type ListingSearchParams } from "@/lib/api";

export default function SearchPage() {
  const [listings, setListings] = useState<Listing[]>([]);
  const [selectedListing, setSelectedListing] = useState<Listing | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [total, setTotal] = useState(0);

  const handleSearch = useCallback(async (params: ListingSearchParams) => {
    setIsLoading(true);
    try {
      const result = await searchListings(params);
      setListings(result.items);
      setTotal(result.total);
    } catch (error) {
      console.error("Search failed:", error);
    } finally {
      setIsLoading(false);
    }
  }, []);

  const handleListingClick = useCallback((listing: Listing) => {
    setSelectedListing(listing);
  }, []);

  return (
    <div className="h-screen flex flex-col">
      {/* Header */}
      <header className="bg-white border-b px-4 py-3">
        <h1 className="text-xl font-bold text-gray-900">PropFair</h1>
      </header>

      {/* Filters */}
      <div className="bg-gray-50 border-b">
        <div className="max-w-screen-2xl mx-auto">
          <ListingFilters onSearch={handleSearch} isLoading={isLoading} />
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Listings panel */}
        <div className="w-1/2 overflow-y-auto p-4 space-y-4">
          <p className="text-sm text-gray-500">
            {total} apartamentos encontrados
          </p>
          <div className="grid gap-4">
            {listings.map((listing) => (
              <ListingCard
                key={listing.id}
                listing={listing}
                onClick={() => handleListingClick(listing)}
                isSelected={selectedListing?.id === listing.id}
              />
            ))}
          </div>
          {listings.length === 0 && !isLoading && (
            <div className="text-center py-12 text-gray-500">
              Usa los filtros para buscar apartamentos
            </div>
          )}
        </div>

        {/* Map panel */}
        <div className="w-1/2 relative">
          <MapContainer
            listings={listings}
            onListingClick={handleListingClick}
            selectedListingId={selectedListing?.id}
          />
        </div>
      </div>
    </div>
  );
}
