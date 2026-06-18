#### `flight_id`
* **Data Type:** String (Unique Primary Key)
* **Description:** A unique alphanumeric transaction identifier assigned to a specific arriving flight sector.
* **Example / Limits:** `FL-1001` (Regex: `^FL-\d{4}$`)
* **Target Impact:** **Zero Predictive Signal.** This is an administrative index. It must be isolated or dropped prior to feeding data into tree-based algorithms to avoid overfitting.

#### `aircraft_type`
* **Data Type:** Categorical
* **Description:** The physical dimensional and structural classification of the arriving aircraft.
* **Categorical Values Explanation:**
    * `Narrowbody`: Single-aisle configurations (e.g., Airbus A320, Boeing 737). Handles standard passenger and luggage profiles with a lightweight ground footprint.
    * `Widebody`: Twin-aisle configurations (e.g., Boeing 777, Airbus A350). Heavy containerized cargo profiles requiring industrial high-lift loaders and significantly larger operational staging windows.
* **Target Impact:** **High Indirect / Scaling Factor.** Shifting from `Narrowbody` to `Widebody` multiplies the baseline physical asset count需求 by up to 3x, compounding the risk of a shortage if local pools are shallow.

#### `terminal_zone`
* **Data Type:** Categorical
* **Description:** The specific geofenced concourse or apron terminal cluster where the flight is scheduled to dock.
* **Categorical Values Explanation:**
    * `Terminal_A`: The main high-volume domestic terminal hub.
    * `Terminal_B`: The international wing characterized by dense wide-body schedules.
    * `Terminal_C`: The regional or low-cost carrier wing optimized for rapid narrow-body rotations.
* **Target Impact:** **Spatial Boundary Constraint.** This feature acts as the localized filter that determines which sub-pool of staging assets (`avail_loaders_zone`, etc.) is mapped against the arriving demand.

#### `arrival_delay_mins`
* **Data Type:** Numerical (Integer)
* **Description:** The minute deviation between the planned scheduled arrival window and the actual block-in time at the gate.
* **Example / Limits:** Min: `-15` (Early), Max: `180` (Severe Delay). Example: `45` (45 minutes late).
* **Target Impact:** **High Combinatorial Risk Multiplier.** High delays force a flight's turnaround window to slide and compress into the subsequent scheduled arrival wave, disrupting pre-staged asset allocations.

#### `actual_arrival_timestamp`
* **Data Type:** Timestamp (`YYYY-MM-DD HH:MM:SS`)
* **Description:** The complete point-in-time date, day, and hour tracking when the aircraft parked at the gate stand.
* **Target Impact:** **Temporal Matrix Root.** Tree-based models extract cyclic patterns from this timestamp. It implicitly flags peak hub banking waves (07:00–09:59 and 16:00–18:59) where the overall airport capacity is naturally strained.

---


#### `required_pushback_tugs`
* **Data Type:** Numerical (Integer)
* **Description:** The exact number of heavy-duty tugs required to push the aircraft back from the gate upon departure.
* **Example / Limits:** Min: `1`, Max: `2`.
* **Target Impact:** **Direct Hard Ceiling.** If this required value handles a deterministic check against `avail_tugs_zone` and finds a deficit, the target variable is instantly forced to `1`.

#### `required_belt_loaders`
* **Data Type:** Numerical (Integer)
* **Description:** The count of mobile conveyor belts or containerized high-loaders needed to service the cargo doors simultaneously.
* **Example / Limits:** Min: `1`, Max: `4`.
* **Target Impact:** **Direct Hard Ceiling.** If `required_belt_loaders` > `avail_loaders_zone` at block-in, the target variable instantly flips to `1`.

#### `required_gpus`
* **Data Type:** Numerical (Integer)
* **Description:** The number of Ground Power Units required to connect and feed continuous electrical power ($115\text{V } 400\text{Hz}$) to the aircraft systems while main engines are off.
* **Example / Limits:** Min: `1`, Max: `2`.
* **Target Impact:** **Direct Hard Ceiling.** Deficits relative to `avail_gpus_zone` guarantee an instant operational shortage flag (`1`).

#### `concurrent_arrivals_30min`
* **Data Type:** Numerical (Integer)
* **Description:** The aggregate number of secondary aircraft landing in the same `terminal_zone` within a rolling 30-minute window of this flight.
* **Example / Limits:** Min: `0` (Isolated arrival), Max: `15` (Extreme congestion wave).
* **Target Impact:** **Highest Direct Positive Correlation.** This serves as the primary metric for resource dilution. As this integer climbs, localized fleet staging layers are thinned out across neighboring gates.

#### `total_zone_baggage_volume`
* **Data Type:** Numerical (Integer)
* **Description:** The total estimated count of checked bags moving through the zone's sorting system during this flight window.
* **Example / Limits:** Min: `50`, Max: `3500` bags.
* **Target Impact:** **Medium Direct Positive Impact.** Massive baggage volumes extend the physical connection time of belt loaders to the aircraft hull, preventing them from being uncoupled and recycled back into the unassigned staging pool.

---


#### `avail_tugs_zone` / `avail_loaders_zone` / `avail_gpus_zone`
* **Data Type:** Numerical (Integer)
* **Description:** The exact inventory count of unassigned, fully functional, stationary equipment parked in the zone's designated safety lines at the arrival timestamp.
* **Example / Limits:** Tugs: `0-25`, Loaders: `0-30`, GPUs: `0-20`.
* **Target Impact:** **Highest Direct Negative Correlation.** As these counts drop toward zero, the mathematical safety buffer of the ramp collapses. Hits of `0` trigger absolute deterministic shortages for incoming flights requiring that asset class.

#### `avg_battery_soc_zone`
* **Data Type:** Numerical (Float)
* **Description:** The averaged State of Charge (battery percentage) across all active electric GSE variants currently sitting in the local terminal pool.
* **Example / Limits:** Min: `15.0%`, Max: `100.0%`.
* **Target Impact:** **High Combinatorial Risk Node.** Low localized battery charge vectors mandate pulling equipment out of rotation for opportunity charging, creating sudden, unpredicted supply cliff-drops mid-shift.

#### `fleet_utilization_ratio`
* **Data Type:** Numerical (Float)
* **Description:** The real-time macro utilization percentage of the airport’s global registered GSE inventory ($0.0 = 0\%$, $1.0 = 100\%$).
* **Example / Limits:** Min: `0.05`, Max: `1.00`. Example: `0.84` (84% of total airport fleet is actively handling flights).
* **Target Impact:** **High Direct Positive Correlation.** Represents systemic pressure. When high, it signifies zero fallback buffers remain to cross-deploy assets from distant terminal boundaries.

#### `gse_operator_on_duty_count`
* **Data Type:** Numerical (Integer)
* **Description:** The total count of certified ramp handling personnel currently clocked into the shift matrix in this specific zone.
* **Example / Limits:** Min: `2`, Max: `40`.
* **Target Impact:** **Human Capital Ceiling Constraint.** Even if physical machinery counts are high, if total concurrent asset requirements across the terminal outnumber the on-duty personnel, effective supply drops to zero, triggering a shortage.

#### `active_fault_code_count_zone`
* **Data Type:** Numerical (Integer)
* **Description:** The total aggregated number of minor diagnostic warning lights (low hydraulic pressure, sensor anomalies) active via telematics in the zone's asset pool.
* **Example / Limits:** Min: `0`, Max: `12`.
* **Target Impact:** **Medium Combinatorial Risk Multiplier.** Acts as an indicator of impending mechanical failure; spikes asset breakdown probability under peak utilization waves or high heat.

---


#### `ambient_temperature_c`
* **Data Type:** Numerical (Float)
* **Description:** Ambient airfield outside air temperature measured at the local meteorological station.
* **Example / Limits:** Min: `-10.0°C`, Max: `48.0°C`.
* **Target Impact:** **High Combinatorial Risk Factor.** High heat profiles (>40°C) degrade battery charging efficiency and strain internal hydraulics, inducing accelerated failure states.

#### `precipitation_intensity`
* **Data Type:** Numerical (Float)
* **Description:** Live liquid or snow precipitation density hitting the airfield tarmac.
* **Example / Limits:** Min: `0.0` (Clear), Max: `30.0 mm/hr` (Torrential downpour).
* **Target Impact:** **Medium Combinatorial Factor.** Rain and slick tarmac trigger strict ramp driving safety speed limitations, extending transit times for equipment across terminal geofences.

#### `wind_speed_knots`
* **Data Type:** Numerical (Float)
* **Description:** Airfield wind velocity metrics.
* **Example / Limits:** Min: `0.0`, Max: `50.0 knots`.
* **Target Impact:** **High Combinatorial Factor.** Extreme crosswinds delay or halt the extension of high-lift container loader mechanisms due to safety regulations, blowing out handling timelines.

---

## The ML Rules Engine: How Features Combine

Your Machine Learning models (such as XGBoost or CatBoost) will lock onto the target by learning these specific, real-world operational interactions embedded within the rows:

* **Logic:** `required_pushback_tugs` > `avail_tugs_zone` OR `required_belt_loaders` > `avail_loaders_zone` OR `required_gpus` > `avail_gpus_zone`.
* **Behavior:** A hard infrastructure limit. The moment raw physical demand outstrips free regional supply, the `gse_shortage_flag` locks to **1**, regardless of weather or timing parameters.

* **Logic:** $\sum(\text{Required Assets Across All Active Flights}) > \text{gse\_operator\_on\_duty\_count}$.
* **Behavior:** Machines cannot drive themselves. If 10 loaders are parked beautifully in the staging lane, but only 3 operators are on shift during a sudden arrival window, the effective supply is choked, forcing an immediate shortage flag (**1**).

* **Logic:** `aircraft_type` == `Widebody` AND `terminal_zone` == `Terminal_B` AND `arrival_delay_mins` > 30 AND `concurrent_arrivals_30min` > 8.
* **Behavior:** A combinatorial trap. A large wide-body plane arriving late crashes into a pre-existing peak travel wave. Because wide-bodies require multi-loader setups, they drain the remaining fleet pool instantly. Shortage probability escalates to **90%**.

* **Logic:** `ambient_temperature_c` > 40.0°C AND `fleet_utilization_ratio` > 0.80 AND `avg_battery_soc_zone` < 40.0%.
* **Behavior:** Scorching ambient heat combined with zero downtime for vehicles accelerates electric battery depletion. Machines fail mid-turnaround or drain out completely, rendering them unusable and forcing the target to **1**.

* **Logic:** (`precipitation_intensity` > 10.0 OR `wind_speed_knots` > 30.0) AND `gse_operator_on_duty_count` < 8.
* **Behavior:** When severe weather rolls onto the apron, vehicles must slow down to a crawl for safety. If operator counts are low, assets take too long to transit across long distances from one terminal sector to another, causing the gate to miss its handling deadline (**1**).