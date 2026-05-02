## How to deploy the changes to Rapsberry pi container

# Step 1. Rebuild the images on your Mac
# cd to root of stock_tracking
docker compose build

# Step 2. Transfer the new images to the Pi
docker save stock_tracking-backend stock_tracking-frontend | ssh aspi@100.64.115.49 "docker load"

# Step 3. Restart the containers on the Pi
ssh aspi@100.64.115.49 "cd ~/stock_tracking && docker compose up -d"

# Docker Compose will detect the new images and recreate only the updated containers. The stocks.json volume is preserved.