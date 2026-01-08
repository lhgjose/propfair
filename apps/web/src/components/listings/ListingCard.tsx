import Image from "next/image";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import type { Listing } from "@/lib/api";
import { Bed, Bath, Car, Maximize } from "lucide-react";

interface ListingCardProps {
  listing: Listing;
  onClick?: () => void;
  isSelected?: boolean;
}

function formatPrice(price: number): string {
  return new Intl.NumberFormat("es-CO", {
    style: "currency",
    currency: "COP",
    maximumFractionDigits: 0,
  }).format(price);
}

export function ListingCard({ listing, onClick, isSelected }: ListingCardProps) {
  return (
    <Card
      className={`cursor-pointer transition-all hover:shadow-lg ${
        isSelected ? "ring-2 ring-blue-500" : ""
      }`}
      onClick={onClick}
    >
      <div className="relative h-48 w-full">
        {listing.images[0] ? (
          <Image
            src={listing.images[0]}
            alt={listing.title}
            fill
            className="object-cover rounded-t-lg"
          />
        ) : (
          <div className="h-full w-full bg-gray-200 rounded-t-lg flex items-center justify-center">
            <span className="text-gray-400">Sin imagen</span>
          </div>
        )}
        {listing.estrato && (
          <Badge className="absolute top-2 right-2">
            Estrato {listing.estrato}
          </Badge>
        )}
      </div>
      <CardContent className="p-4">
        <div className="space-y-2">
          <h3 className="font-semibold text-lg line-clamp-1">{listing.title}</h3>
          <p className="text-sm text-gray-500 line-clamp-1">
            {listing.neighborhood}, {listing.city}
          </p>
          <p className="text-xl font-bold text-green-600">
            {formatPrice(listing.price)}
            <span className="text-sm font-normal text-gray-500">/mes</span>
          </p>
          {listing.admin_fee && (
            <p className="text-sm text-gray-500">
              Admin: {formatPrice(listing.admin_fee)}
            </p>
          )}
          <div className="flex items-center gap-4 text-sm text-gray-600 pt-2">
            <span className="flex items-center gap-1">
              <Bed className="h-4 w-4" />
              {listing.bedrooms}
            </span>
            <span className="flex items-center gap-1">
              <Bath className="h-4 w-4" />
              {listing.bathrooms}
            </span>
            <span className="flex items-center gap-1">
              <Car className="h-4 w-4" />
              {listing.parking_spaces}
            </span>
            <span className="flex items-center gap-1">
              <Maximize className="h-4 w-4" />
              {listing.area}m²
            </span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
