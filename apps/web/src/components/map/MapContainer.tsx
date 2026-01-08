"use client";

import { useState, useCallback } from "react";
import Map, { NavigationControl, ViewStateChangeEvent } from "react-map-gl/maplibre";
import DeckGL from "@deck.gl/react";
import { ScatterplotLayer } from "@deck.gl/layers";
import type { Listing } from "@/lib/api";
import "maplibre-gl/dist/maplibre-gl.css";

interface MapContainerProps {
  listings: Listing[];
  onListingClick?: (listing: Listing) => void;
  selectedListingId?: string;
}

const INITIAL_VIEW_STATE = {
  latitude: 4.6097,
  longitude: -74.0817,
  zoom: 12,
  pitch: 0,
  bearing: 0,
};

export function MapContainer({
  listings,
  onListingClick,
  selectedListingId,
}: MapContainerProps) {
  const [viewState, setViewState] = useState(INITIAL_VIEW_STATE);

  const handleViewStateChange = useCallback(
    (e: ViewStateChangeEvent) => {
      setViewState(e.viewState);
    },
    []
  );

  const layers = [
    new ScatterplotLayer({
      id: "listings-layer",
      data: listings,
      getPosition: (d: Listing) => [d.longitude, d.latitude],
      getRadius: (d: Listing) => (d.id === selectedListingId ? 150 : 100),
      getFillColor: (d: Listing) => {
        if (d.id === selectedListingId) return [59, 130, 246, 255]; // Blue
        return [16, 185, 129, 200]; // Green
      },
      pickable: true,
      onClick: ({ object }) => {
        if (object && onListingClick) {
          onListingClick(object);
        }
      },
      radiusMinPixels: 8,
      radiusMaxPixels: 20,
    }),
  ];

  return (
    <div className="relative w-full h-full">
      <DeckGL
        viewState={viewState}
        onViewStateChange={handleViewStateChange as any}
        controller={true}
        layers={layers}
      >
        <Map
          mapStyle="https://basemaps.cartocdn.com/gl/positron-gl-style/style.json"
        >
          <NavigationControl position="top-right" />
        </Map>
      </DeckGL>
    </div>
  );
}
