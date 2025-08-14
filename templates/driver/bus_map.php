<?php
$content = '
<div class="dashboard-container">
  <h2 class="dashboard-title">Bus Location</h2>
  <div class="card">
    <?php if ($bus): ?>
      <p><strong>Bus:</strong> <?php echo htmlspecialchars($bus["number_plate"]); ?></p>
      <div id="map" style="height: 400px; margin: 20px 0;"></div>
      <form id="location-form">
        <input type="hidden" id="bus_id" name="bus_id" value="<?php echo $bus["id"]; ?>">
        <div style="margin-bottom: 15px;">
          <label for="lat">Latitude:</label>
          <input type="text" id="lat" name="lat" required style="width: 100%; padding: 8px; margin-top: 5px;">
        </div>
        <div style="margin-bottom: 15px;">
          <label for="lng">Longitude:</label>
          <input type="text" id="lng" name="lng" required style="width: 100%; padding: 8px; margin-top: 5px;">
        </div>
        <button type="submit" class="btn btn-primary">Update Location</button>
      </form>
    <?php else: ?>
      <p>No bus assigned to you.</p>
    <?php endif; ?>
  </div>
</div>

<script>
// Simple form submission for updating bus location
document.getElementById("location-form").addEventListener("submit", function(e) {
  e.preventDefault();
  
  const bus_id = document.getElementById("bus_id").value;
  const lat = document.getElementById("lat").value;
  const lng = document.getElementById("lng").value;
  
  if (!bus_id || !lat || !lng) {
    alert("Please fill in all fields");
    return;
  }
  
  // In a real application, you would send this data to your server
  // For now, we\'ll just show an alert
  alert("Location would be updated in a real application. Bus ID: " + bus_id + ", Lat: " + lat + ", Lng: " + lng);
});

// In a real application, you would use a mapping library like Google Maps or Leaflet
// to display the actual map and bus location
</script>

<style>
.dashboard-container {
  max-width: 900px;
  margin: 40px auto;
  padding: 24px;
}
.dashboard-title {
  color: var(--primary);
  margin-bottom: 24px;
}
.card {
  background: var(--card-bg);
  border-radius: var(--radius);
  box-shadow: 0 2px 8px rgba(0,0,0,0.04);
  padding: 24px;
  margin-bottom: 24px;
}
</style>
';

include TEMPLATES_PATH . '/base.php';