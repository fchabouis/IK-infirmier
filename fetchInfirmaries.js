import { createClient } from "@supabase/supabase-js";

const SUPABASE_URL = "https://roywfsncxupoouzgwmni.supabase.co";
const SUPABASE_KEY =
  "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InJveXdmc25jeHVwb291emd3bW5pIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzI1NDU3MTcsImV4cCI6MjA4ODEyMTcxN30.3eLtV4Ou7clPyXgiQr-ptjRF8Py0r2YeD9oZ3r59UOw";

const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);

export async function fetchNearby(lat, lng, limit = 10) {
  const { data } = await supabase.rpc("nearby_infirmaries", {
    lat,
    lng,
    limit_n: limit,
  });
  return data;
}
