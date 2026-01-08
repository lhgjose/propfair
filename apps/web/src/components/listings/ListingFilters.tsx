"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { ListingSearchParams } from "@/lib/api";

interface ListingFiltersProps {
  onSearch: (params: ListingSearchParams) => void;
  isLoading?: boolean;
}

export function ListingFilters({ onSearch, isLoading }: ListingFiltersProps) {
  const [filters, setFilters] = useState<ListingSearchParams>({
    city: "Bogotá",
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSearch(filters);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4 p-4 bg-white rounded-lg shadow">
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="space-y-2">
          <Label htmlFor="min_price">Precio mínimo</Label>
          <Input
            id="min_price"
            type="number"
            placeholder="$ 1.000.000"
            value={filters.min_price || ""}
            onChange={(e) =>
              setFilters({ ...filters, min_price: Number(e.target.value) || undefined })
            }
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="max_price">Precio máximo</Label>
          <Input
            id="max_price"
            type="number"
            placeholder="$ 5.000.000"
            value={filters.max_price || ""}
            onChange={(e) =>
              setFilters({ ...filters, max_price: Number(e.target.value) || undefined })
            }
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="bedrooms">Habitaciones</Label>
          <Select
            value={filters.bedrooms?.toString()}
            onValueChange={(value) =>
              setFilters({ ...filters, bedrooms: Number(value) || undefined })
            }
          >
            <SelectTrigger id="bedrooms">
              <SelectValue placeholder="Cualquiera" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">1+</SelectItem>
              <SelectItem value="2">2+</SelectItem>
              <SelectItem value="3">3+</SelectItem>
              <SelectItem value="4">4+</SelectItem>
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="estrato">Estrato</Label>
          <Select
            value={filters.estrato?.toString()}
            onValueChange={(value) =>
              setFilters({ ...filters, estrato: Number(value) || undefined })
            }
          >
            <SelectTrigger id="estrato">
              <SelectValue placeholder="Cualquiera" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="1">1</SelectItem>
              <SelectItem value="2">2</SelectItem>
              <SelectItem value="3">3</SelectItem>
              <SelectItem value="4">4</SelectItem>
              <SelectItem value="5">5</SelectItem>
              <SelectItem value="6">6</SelectItem>
            </SelectContent>
          </Select>
        </div>
      </div>

      <Button type="submit" className="w-full" disabled={isLoading}>
        {isLoading ? "Buscando..." : "Buscar"}
      </Button>
    </form>
  );
}
