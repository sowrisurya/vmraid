import vmraid

def execute():
	vmraid.db.multisql({
		"mariadb": "ALTER  TABLE `__Auth` MODIFY `password` TEXT NOT NULL",
		"postgres": 'ALTER TABLE "__Auth" ALTER COLUMN "password" TYPE TEXT'
	})
