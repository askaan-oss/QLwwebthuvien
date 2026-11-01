IF OBJECT_ID(N'dbo.notifications', N'U') IS NULL
BEGIN
 CREATE TABLE dbo.notifications (
 notification_id BIGINT IDENTITY(1,1) CONSTRAINT PK_notifications PRIMARY KEY,
 customer_id BIGINT NULL,
 title NVARCHAR(255) NOT NULL,
 message NVARCHAR(MAX) NOT NULL,
 type VARCHAR(50) NULL,
 is_read BIT NOT NULL DEFAULT 0,
 created_at DATETIME NOT NULL DEFAULT GETDATE(),
 read_at DATETIME NULL,
 CONSTRAINT FK_notifications_customers FOREIGN KEY(customer_id) REFERENCES dbo.customers(customer_id) ON DELETE CASCADE
 );
END;
IF NOT EXISTS(SELECT 1 FROM sys.indexes WHERE object_id=OBJECT_ID(N'dbo.notifications') AND name=N'IX_notifications_customer_created')
 CREATE INDEX IX_notifications_customer_created ON dbo.notifications(customer_id, created_at DESC);
