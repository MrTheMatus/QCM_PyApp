-- Insert into Material table
INSERT INTO Material (material_id, material_name, density) VALUES
(1, 'Silver', 10.49),
(2, 'Gold', 19.32);

-- Insert into SetupConstants table
INSERT INTO SetupConstants (id, quartz_density, quartz_shear_modulus, quartz_area, tooling_factor, description, created_at) VALUES
(1, 2.648, 44, 28.27, 1, 'Default@WUST', '2024-12-28 02:00:23');
