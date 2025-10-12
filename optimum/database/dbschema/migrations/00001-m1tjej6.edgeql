CREATE MIGRATION m1tjej6dim6posklrim5dcksg25pzizwp36lr45bkwgskhn73y5rpa
    ONTO initial
{
  CREATE SCALAR TYPE default::BusinessArea EXTENDING enum<MEC, CHA, ERA, SGN, SYS, ZO1, ZO2, ZO3, EXT>;
  CREATE SCALAR TYPE default::Currency EXTENDING enum<EUR, USD, GBP, CHF, SEK, NOK, DKK, PLN, CZK, HUF>;
  CREATE SCALAR TYPE default::EquipmentId EXTENDING std::sequence {
      CREATE CONSTRAINT std::max_ex_value(20000000);
      CREATE CONSTRAINT std::min_ex_value(10000000);
  };
  CREATE SCALAR TYPE default::FailureImpact EXTENDING enum<UNACCEPTABLE, MAJOR, SIGNIFICANT, ACCEPTABLE>;
  CREATE SCALAR TYPE default::FailureTolerance EXTENDING enum<`8H`, `24/48H`, DAYS, WEEKS>;
  CREATE SCALAR TYPE default::ItemCategory EXTENDING enum<SPARE, TOOL, CONSUMABLE, CHEMICAL, PACKAGING>;
  CREATE SCALAR TYPE default::ItemRegulatoryInfo EXTENDING enum<FOOD, FEED, ATEX>;
  CREATE SCALAR TYPE default::ItemUnit EXTENDING enum<UNIT, BUNDLE, KG, L, M>;
  CREATE SCALAR TYPE default::NotificationId EXTENDING std::sequence {
      CREATE CONSTRAINT std::max_ex_value(50000000);
      CREATE CONSTRAINT std::min_ex_value(40000000);
  };
  CREATE SCALAR TYPE default::OperationId EXTENDING std::sequence {
      CREATE CONSTRAINT std::max_ex_value(40000000);
      CREATE CONSTRAINT std::min_ex_value(30000000);
  };
  CREATE SCALAR TYPE default::PlantLocation EXTENDING enum<BR, EP, ET, MA, RS, RC>;
  CREATE SCALAR TYPE default::PurchasedItemId EXTENDING std::sequence {
      CREATE CONSTRAINT std::max_ex_value(30000000);
      CREATE CONSTRAINT std::min_ex_value(20000000);
  };
  CREATE SCALAR TYPE default::StaffCode EXTENDING std::str {
      CREATE CONSTRAINT std::regexp(r'^SL\d{5}$');
  };
  CREATE FUTURE simple_scoping;
  CREATE TYPE default::OperationalPosition {
      CREATE REQUIRED PROPERTY description: std::str {
          CREATE CONSTRAINT std::max_len_value(50);
      };
      CREATE REQUIRED PROPERTY is_active: std::bool {
          SET default := true;
      };
      CREATE REQUIRED PROPERTY position_id: std::str {
          CREATE CONSTRAINT std::exclusive;
          CREATE CONSTRAINT std::max_len_value(20);
      };
      CREATE OPTIONAL PROPERTY process_area: std::str {
          CREATE CONSTRAINT std::max_len_value(20);
      };
      CREATE OPTIONAL PROPERTY subunit: std::str {
          CREATE CONSTRAINT std::max_len_value(20);
      };
      CREATE OPTIONAL PROPERTY unit: std::str {
          CREATE CONSTRAINT std::max_len_value(20);
      };
  };
  CREATE TYPE default::VendorReference {
      CREATE REQUIRED PROPERTY vendor_identifier: std::str {
          CREATE CONSTRAINT std::max_len_value(20);
      };
      CREATE OPTIONAL PROPERTY vendor_instructions: std::str;
      CREATE OPTIONAL PROPERTY vendor_item_currency: default::Currency;
      CREATE OPTIONAL PROPERTY vendor_item_lead_time_days: std::int16;
      CREATE OPTIONAL PROPERTY vendor_item_price: std::float32 {
          CREATE CONSTRAINT std::min_value(0.0);
      };
      CREATE OPTIONAL PROPERTY vendor_item_reference: std::str;
      CREATE OPTIONAL PROPERTY vendor_order_quantity: std::int16;
  };
  CREATE TYPE default::PurchasedItem {
      CREATE OPTIONAL MULTI LINK vendor_references: default::VendorReference;
      CREATE REQUIRED PROPERTY category: default::ItemCategory;
      CREATE REQUIRED PROPERTY description: std::str;
      CREATE REQUIRED PROPERTY is_active: std::bool {
          SET default := true;
      };
      CREATE OPTIONAL PROPERTY is_maintainable: std::bool {
          SET default := false;
      };
      CREATE REQUIRED PROPERTY item_id: default::PurchasedItemId {
          CREATE CONSTRAINT std::exclusive;
      };
      CREATE REQUIRED PROPERTY plant_location: default::PlantLocation;
      CREATE OPTIONAL PROPERTY quantity_in_stock: std::int16 {
          CREATE CONSTRAINT std::min_value(0);
      };
      CREATE OPTIONAL PROPERTY regulatory_info: default::ItemRegulatoryInfo;
      CREATE OPTIONAL PROPERTY reorder_level: std::int16 {
          CREATE CONSTRAINT std::min_value(0);
      };
      CREATE OPTIONAL PROPERTY specifications: std::str;
      CREATE OPTIONAL PROPERTY storage_location: std::str {
          CREATE CONSTRAINT std::max_len_value(20);
      };
      CREATE OPTIONAL PROPERTY unit_of_measure: default::ItemUnit;
  };
  CREATE TYPE default::Equipment {
      CREATE OPTIONAL MULTI LINK components: default::Equipment;
      CREATE OPTIONAL LINK operational_position: default::OperationalPosition;
      CREATE OPTIONAL LINK purchased_item: default::PurchasedItem;
      CREATE OPTIONAL MULTI LINK spare_parts: default::PurchasedItem;
      CREATE OPTIONAL PROPERTY business_area: default::BusinessArea;
      CREATE REQUIRED PROPERTY description: std::str {
          CREATE CONSTRAINT std::max_len_value(50);
      };
      CREATE REQUIRED PROPERTY equipment_id: default::EquipmentId {
          CREATE CONSTRAINT std::exclusive;
      };
      CREATE REQUIRED PROPERTY failure_impact: default::FailureImpact;
      CREATE REQUIRED PROPERTY failure_tolerance: default::FailureTolerance;
      CREATE OPTIONAL PROPERTY installation_date: std::datetime;
      CREATE REQUIRED PROPERTY is_active: std::bool {
          SET default := true;
      };
      CREATE OPTIONAL PROPERTY location_mark: std::str;
      CREATE OPTIONAL PROPERTY manufacturer: std::str;
      CREATE OPTIONAL PROPERTY model_number: std::str;
      CREATE REQUIRED PROPERTY plant_location: default::PlantLocation;
      CREATE OPTIONAL PROPERTY serial_number: std::str;
  };
  CREATE TYPE default::StaffMember {
      CREATE OPTIONAL PROPERTY business_area: default::BusinessArea;
      CREATE OPTIONAL PROPERTY email: std::str;
      CREATE REQUIRED PROPERTY first_name: std::str;
      CREATE REQUIRED PROPERTY is_active: std::bool {
          SET default := true;
      };
      CREATE REQUIRED PROPERTY last_name: std::str;
      CREATE OPTIONAL PROPERTY pay_index: std::float32 {
          CREATE CONSTRAINT std::min_value(0.0);
      };
      CREATE OPTIONAL PROPERTY phone: std::str;
      CREATE OPTIONAL PROPERTY plant_location: default::PlantLocation;
      CREATE OPTIONAL PROPERTY position: std::str;
      CREATE REQUIRED PROPERTY staff_id: default::StaffCode {
          CREATE CONSTRAINT std::exclusive;
      };
  };
  CREATE TYPE default::Operation {
      CREATE OPTIONAL MULTI LINK materials: default::PurchasedItem;
      CREATE OPTIONAL MULTI LINK performed_by: default::StaffMember;
      CREATE OPTIONAL MULTI LINK tools: default::PurchasedItem;
      CREATE OPTIONAL PROPERTY accounting_carryover: std::float32;
      CREATE OPTIONAL PROPERTY actual_external_cost: std::float32 {
          CREATE CONSTRAINT std::min_value(0.0);
      };
      CREATE OPTIONAL PROPERTY actual_labor_cost: std::float32 {
          CREATE CONSTRAINT std::min_value(0.0);
      };
      CREATE OPTIONAL PROPERTY actual_material_cost: std::float32 {
          CREATE CONSTRAINT std::min_value(0.0);
      };
      CREATE REQUIRED PROPERTY actual_total_costs := (((((.actual_labor_cost ?? 0.0) + (.actual_material_cost ?? 0.0)) + (.actual_external_cost ?? 0.0)) + (.accounting_carryover ?? 0.0)));
      CREATE REQUIRED PROPERTY activity: std::str {
          CREATE CONSTRAINT std::one_of('CLEAN', 'PREVENT', 'PREPARE', 'ACCESS', 'REPAIR');
      };
      CREATE OPTIONAL PROPERTY actual_labor_hours: std::float32 {
          CREATE CONSTRAINT std::min_value(0.0);
      };
      CREATE OPTIONAL PROPERTY business_area: default::BusinessArea;
      CREATE OPTIONAL PROPERTY completed_date: std::datetime;
      CREATE REQUIRED PROPERTY cost_allocation: std::str {
          CREATE CONSTRAINT std::max_len_value(20);
      };
      CREATE REQUIRED PROPERTY cost_currency: default::Currency {
          SET default := 'EUR';
      };
      CREATE REQUIRED PROPERTY defines_plan: std::bool {
          SET default := false;
      };
      CREATE REQUIRED PROPERTY description: std::str;
      CREATE OPTIONAL PROPERTY frequency: std::str {
          CREATE CONSTRAINT std::one_of('DAY', 'MONTH', 'YEAR');
      };
      CREATE OPTIONAL PROPERTY interval: std::int16;
      CREATE REQUIRED PROPERTY operation_id: default::OperationId {
          CREATE CONSTRAINT std::exclusive;
      };
      CREATE REQUIRED PROPERTY parent_id: std::int64;
      CREATE OPTIONAL PROPERTY planned_external_cost: std::float32 {
          CREATE CONSTRAINT std::min_value(0.0);
      };
      CREATE OPTIONAL PROPERTY planned_labor_cost: std::float32 {
          CREATE CONSTRAINT std::min_value(0.0);
      };
      CREATE OPTIONAL PROPERTY planned_labor_hours: std::float32 {
          CREATE CONSTRAINT std::min_value(0.0);
      };
      CREATE OPTIONAL PROPERTY planned_material_cost: std::float32 {
          CREATE CONSTRAINT std::min_value(0.0);
      };
      CREATE OPTIONAL PROPERTY planned_total_costs: std::float32 {
          CREATE CONSTRAINT std::min_value(0.0);
      };
      CREATE OPTIONAL PROPERTY recurrency_count: std::int16;
      CREATE OPTIONAL PROPERTY recurrency_target: std::int16;
      CREATE OPTIONAL PROPERTY scheduled_date: std::datetime;
      CREATE REQUIRED PROPERTY status: std::str {
          CREATE CONSTRAINT std::one_of('OPEN', 'PLANNED', 'HOLD', 'DONE', 'SUPPR');
      };
      CREATE OPTIONAL PROPERTY subcontractor: std::str {
          CREATE CONSTRAINT std::max_len_value(20);
      };
  };
  ALTER TYPE default::Equipment {
      CREATE OPTIONAL MULTI LINK planned_operations: default::Operation;
  };
  CREATE TYPE default::Notification {
      CREATE REQUIRED LINK equipment: default::Equipment;
      CREATE REQUIRED LINK created_by: default::StaffMember;
      CREATE OPTIONAL MULTI LINK operations: default::Operation;
      CREATE REQUIRED PROPERTY created_at: std::datetime;
      CREATE OPTIONAL PROPERTY long_text: std::str;
      CREATE REQUIRED PROPERTY notification_id: default::NotificationId {
          CREATE CONSTRAINT std::exclusive;
      };
      CREATE REQUIRED PROPERTY short_text: std::str;
      CREATE REQUIRED PROPERTY status: std::str {
          CREATE CONSTRAINT std::one_of('NEW', 'PLANNED', 'HOLD', 'CLOSED');
      };
      CREATE OPTIONAL PROPERTY updates_history: array<std::str>;
  };
  CREATE TYPE default::PurchaseOrderWorkflow {
      CREATE OPTIONAL LINK operation: default::Operation;
      CREATE OPTIONAL LINK approved_by: default::StaffMember;
      CREATE OPTIONAL LINK ordered_by: default::StaffMember;
      CREATE OPTIONAL LINK requested_by: default::StaffMember;
      CREATE REQUIRED PROPERTY status: std::str {
          CREATE CONSTRAINT std::one_of('SAVED', 'REQUESTED', 'APPROVED', 'ORDERED', 'ACCEPTED', 'CLOSED', 'CANCELLED');
      };
  };
  CREATE TYPE default::PurchaseOrderAgreement {
      CREATE REQUIRED MULTI LINK owners: default::StaffMember;
      CREATE OPTIONAL MULTI LINK workflows: default::PurchaseOrderWorkflow;
      CREATE REQUIRED PROPERTY agreement_id: std::int64 {
          CREATE CONSTRAINT std::exclusive;
      };
      CREATE OPTIONAL PROPERTY currency: default::Currency {
          SET default := 'EUR';
      };
      CREATE REQUIRED PROPERTY description: std::str {
          CREATE CONSTRAINT std::max_len_value(40);
      };
      CREATE OPTIONAL PROPERTY general_terms: std::str;
      CREATE OPTIONAL PROPERTY hse_terms: std::str;
      CREATE REQUIRED PROPERTY is_active: std::bool {
          SET default := true;
      };
      CREATE OPTIONAL PROPERTY is_template: std::bool {
          SET default := false;
      };
      CREATE OPTIONAL PROPERTY legal_terms: std::str;
      CREATE OPTIONAL PROPERTY lump_sum: std::float32 {
          CREATE CONSTRAINT std::min_value(0.0);
      };
      CREATE OPTIONAL PROPERTY preamble: std::str;
      CREATE OPTIONAL PROPERTY purchase_terms: std::str;
      CREATE OPTIONAL PROPERTY quality_terms: std::str;
      CREATE REQUIRED PROPERTY revision: std::int16 {
          CREATE CONSTRAINT std::min_value(1);
      };
      CREATE REQUIRED PROPERTY revision_date: std::datetime;
      CREATE OPTIONAL PROPERTY technical_terms: std::str;
      CREATE OPTIONAL PROPERTY valid_from: std::datetime;
      CREATE OPTIONAL PROPERTY valid_to: std::datetime;
      CREATE REQUIRED PROPERTY vendor: std::str;
      CREATE OPTIONAL PROPERTY vendor_contact: std::str;
      CREATE OPTIONAL PROPERTY vendor_email: std::str;
      CREATE OPTIONAL PROPERTY vendor_phone: std::str;
  };
  CREATE TYPE default::PurchaseOrderPosition {
      CREATE REQUIRED LINK agreement: default::PurchaseOrderAgreement;
      CREATE OPTIONAL LINK purchased_item: default::PurchasedItem;
      CREATE OPTIONAL PROPERTY currency: default::Currency {
          SET default := 'EUR';
      };
      CREATE OPTIONAL PROPERTY delivery_date: std::datetime;
      CREATE OPTIONAL PROPERTY description: std::str;
      CREATE OPTIONAL PROPERTY detailed_instructions: std::str;
      CREATE OPTIONAL PROPERTY discount: std::float32 {
          CREATE CONSTRAINT std::min_value(0.0);
      };
      CREATE REQUIRED PROPERTY ordered_quantity: std::float32 {
          CREATE CONSTRAINT std::min_value(0.0);
      };
      CREATE REQUIRED PROPERTY unit_price: std::float32 {
          CREATE CONSTRAINT std::min_value(0.0);
      };
      CREATE REQUIRED PROPERTY total_price := (((.ordered_quantity * .unit_price) - (.discount ?? 0.0)));
      CREATE REQUIRED PROPERTY final_acceptance: std::bool {
          SET default := false;
      };
      CREATE REQUIRED PROPERTY is_active: std::bool {
          SET default := true;
      };
      CREATE REQUIRED PROPERTY position_number: std::int16;
      CREATE OPTIONAL PROPERTY received_quantity: std::float32 {
          CREATE CONSTRAINT std::min_value(0.0);
      };
  };
  ALTER TYPE default::PurchaseOrderWorkflow {
      CREATE OPTIONAL MULTI LINK positions: default::PurchaseOrderPosition;
  };
};
