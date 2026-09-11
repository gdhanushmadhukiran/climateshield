"""Spatial and GeoJSON validation tests."""

from shapely.geometry import Polygon, Point


def test_spatial_zone_geometry_and_ordering(client):
    response = client.get("/api/v1/risk/zones")
    assert response.status_code == 200
    zones = response.json()

    for zone in zones:
        centroid = zone["centroid"]
        lat = centroid["lat"]
        lng = centroid["lng"]

        # Visakhapatnam region check (lat ~ 17.6 - 17.8, lng ~ 83.1 - 83.4)
        assert 17.0 <= lat <= 18.0, f"Latitude {lat} inverted or out of bounds for {zone['name']}"
        assert 83.0 <= lng <= 84.0, f"Longitude {lng} inverted or out of bounds for {zone['name']}"

        poly_coords = zone["polygon"]
        assert len(poly_coords) >= 4, "Polygon must have at least 4 points (closed ring)"

        # Check coordinate order: [longitude, latitude]
        for coord in poly_coords:
            coord_lng, coord_lat = coord[0], coord[1]
            assert 83.0 <= coord_lng <= 84.0, f"Expected longitude in position 0, got {coord_lng}"
            assert 17.0 <= coord_lat <= 18.0, f"Expected latitude in position 1, got {coord_lat}"

        # Verify geometric validity using Shapely
        shapely_poly = Polygon(poly_coords)
        assert shapely_poly.is_valid, f"Polygon geometry invalid for zone {zone['id']}"

        # Centroid should be near the polygon
        centroid_point = Point(lng, lat)
        assert shapely_poly.distance(centroid_point) < 0.1
