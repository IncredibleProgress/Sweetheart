CREATE MIGRATION m1grdkq2kr45t6y7oarpreawcfqlabyxgko4boaomzillix5yny2ma
    ONTO m1tjej6dim6posklrim5dcksg25pzizwp36lr45bkwgskhn73y5rpa
{
  ALTER TYPE default::Notification {
      ALTER PROPERTY short_text {
          CREATE CONSTRAINT std::max_len_value(50);
      };
  };
  ALTER TYPE default::PurchaseOrderAgreement {
      ALTER PROPERTY description {
          DROP CONSTRAINT std::max_len_value(40);
      };
  };
  ALTER TYPE default::PurchaseOrderAgreement {
      ALTER PROPERTY description {
          CREATE CONSTRAINT std::max_len_value(50);
      };
      ALTER PROPERTY vendor {
          CREATE CONSTRAINT std::max_len_value(20);
      };
  };
};
